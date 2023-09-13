from bs4 import BeautifulSoup
import json
from playwright.sync_api import sync_playwright

def extract_course_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        # click heading. no-op, but will ensure the page loaded
        page.get_by_role("heading", name="Welcome to Guitar Wisdom").click()
        # Sleep for 30 seconds to let me sign in / login
        page.wait_for_timeout(30 * 1000)
        
        # Scroll to load all lazily loaded content
        for i in range(6):
            # (positive is scrolling down, negative is scrolling up)
            page.mouse.wheel(0, 15000)
            page.wait_for_timeout(2000)
            i += 1
        # page.mouse.wheel(0, -1 * 15000 * 6)

        html = page.content()

        # Parse the HTML content with BeautifulSoup
        rootSoup = BeautifulSoup(html, 'html.parser')

        # Initialize the course content dictionary
        course_content = []

        # Find section titles and urls
        section_title_elems = rootSoup.select("h1.head.primary.site-font-primary-color.margin-right-medium.horizontal-row-header.column.small-16.medium-12")
        section_url_elems = rootSoup.select("a.site-font-primary-color.view-more-link")

        # Adjust the range to start from section 4 cause internet died kek
        # section_title_elems = section_title_elems[4:]
        # section_url_elems = section_url_elems[4:]


        for section_index in range(len(section_title_elems)):
            section_title = section_title_elems[section_index].text.strip()
            print('Scraping section index: ', section_index)
            print('Scraping section w/ title: ', section_title)

            section_url = section_url_elems[section_index]["href"]
            # print('section_url', section_url)

            # open section url
            page.goto(section_url)
            # Sleep for ~3 seconds to ensure the page is fully loaded
            page.wait_for_timeout(2400)

            # Find all video cards
            html = page.content()
            section_soup = BeautifulSoup(html, 'html.parser')
            video_cards = section_soup.select("div.browse-item-card")
            # # print('video cards: ', video_cards)

            # Initialize the section_videos list
            section_videos = []

            # Iterate through video cards and extract video information
            for video_index, video_card in enumerate(video_cards):
                print('Scraping video card index:', video_index)
                video_title_elem = video_card.select("div.site-font-primary-color.browse-item-title")[0]
                # # print('video_title_elem: ', video_title_elem)
                video_page_url_elem = video_card.find("a")
                video_page_url = video_page_url_elem.get('href')
                # print('video_page_url: ', video_page_url)

                # Subscribe to "response" events. This will allow us to scrape the download URL later
                video_page_url_responses = []
                page.on("response", lambda response: video_page_url_responses.append(response))
                page.goto(video_page_url)
                # page.wait_for_timeout(10_000) # wait for quite a bit to let all responses with download urls to come in. actually not needed unless downloading within this very script, because the collected download urls will not be valid without active user session

                # use BeautifulSoup to search for Show More button. If it doesn't exist, we can skip over Playwright auto-retrying to click it when it never exists
                video_page_soup = BeautifulSoup(page.content(),  'html.parser')
                show_more_button = video_page_soup.select("label.read-more-trigger")
                print('show_more_button', show_more_button)
                print('len show_more_button', len(show_more_button))
                if len(show_more_button) > 0:
                    try:
                        show_more_button = page.wait_for_selector("text=Show more", timeout=500)
                        if show_more_button:
                            show_more_button.click()
                    except:
                        # print("No 'Show More' button found.")
                        pass

                video_description_elem = video_page_soup.select("div.text.site-font-secondary-color")[0]

                if video_title_elem and video_description_elem and video_page_url_elem:
                    # print('video_title_elem', video_title_elem)
                    video_title = video_title_elem.text.strip()
                    print('video_title: ', video_title)

                    video_description = video_description_elem.text.strip()
                    # print('video_description', video_description)

                    # Inspect get requests to find vimeo request and scrape download link
                    requestURLSearchString = 'player.vimeo.com/video'
                    matching_response = None
                    for response in video_page_url_responses:
                        # print('video_page_url_responses: ', response)
                        if requestURLSearchString in response.url:
                            matching_response = response
                            break
                    print('video response: ', matching_response)
                    # video_download_url = ''
                    # if matching_response is not None:
                    #     response_json = matching_response.json()
                    #     # print('response_json: ', response_json)
                    #     # get the URL for the 720p video. its 60FPS, but smaller than 1080p.
                    #     progressive_json_section = response_json['request']['files']['progressive']
                    #     # print('progressive_json_section: ', progressive_json_section)
                    #     for item in progressive_json_section:
                    #         # print('item [width]: ', item['width'])
                    #         if item['width'] == 1280 and item['height'] == 720:
                    #             video_download_url = item['url']
                    #             # print('video_download_url',video_download_url)
                    #             break

                    # Create a video dictionary
                    video_info = {
                        "video_title": video_title,
                        "video_index": video_index,
                        "video_description": video_description,
                        "video_page_url": video_page_url,
                        # "video_download_url": video_download_url,
                    }

                    # Add the video dictionary to the section_videos list
                    section_videos.append(video_info)
                    print('')

            # Add section information to the course_content dictionary
            section_info = {
                "section_title": section_title,
                "section_url": section_url,
                "section_index": section_index,
                "section_videos": section_videos,
            }
            with open(f'section-{section_index}.json', 'w') as json_file:
                json.dump(section_info, json_file)

            course_content.append(section_info)

            print(f'Section {section_index} scraped')
            print('Course content so far: ', course_content)
            print('')

        # Close the browser
        browser.close()

        return course_content

if __name__ == "__main__":
    url = "https://tomovhxtv.vhx.tv/browse"  # Replace with the URL of the HTML page
    course_content_dict = extract_course_content(url)

    # print the course content dictionary
    print('Final course content dict: ')
    print(course_content_dict)
    with open('course_content.json', 'w') as json_file:
        json.dump(course_content_dict, json_file)
    print(f'Saved final course content dict to course_content.json')

