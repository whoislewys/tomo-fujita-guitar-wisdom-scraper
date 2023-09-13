from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def extract_course_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=2)
        page = browser.new_page()
        page.goto(url)
        # click heading. no-op, but will ensure the page loaded
        page.get_by_role("heading", name="Welcome to Guitar Wisdom").click()
        # Sleep for 3 seconds to ensure the page is fully loaded
        page.wait_for_timeout(3000)
        
        # for i in range(6):
        #     # (positive is scrolling down, negative is scrolling up)
        #     page.mouse.wheel(0, 15000)
        #     page.wait_for_timeout(2000)
        #     i += 1
        # page.mouse.wheel(0, -1 * 15000 * 6)

        html = page.content()

        # Parse the HTML content with BeautifulSoup
        rootSoup = BeautifulSoup(html, 'html.parser')

        # Initialize the course content dictionary
        course_content = {}

        # Find first section title and url
        section_title_elem = rootSoup.select("h1.head.primary.site-font-primary-color.margin-right-medium.horizontal-row-header.column.small-16.medium-12")[0]
        section_title = section_title_elem.text.strip()
        print('section title', section_title)

        section_url_elem = rootSoup.select("a.site-font-primary-color")[0]
        section_url = section_url_elem["href"]
        print('section_url', section_url)

        # open section url
        page.goto(section_url)
        # Sleep for 3 seconds to ensure the page is fully loaded
        page.wait_for_timeout(3000)

        # Find all video cards
        html = page.content()
        section_soup = BeautifulSoup(html, 'html.parser')
        video_cards = section_soup.select("div.browse-item-card")
        # print('video cards: ', video_cards)

        # Initialize the section_videos list
        section_videos = []

        # Iterate through video cards and extract video information
        for index, video_card in enumerate(video_cards):
            print('Scraping video card index:', index)

            video_title_elem = video_card.select("div.site-font-primary-color.browse-item-title")[0]
            # print('video_title_elem: ', video_title_elem)
            video_page_url_elem = video_card.find("a")
            video_page_href = video_page_url_elem.get('href')
            print('video href: ', video_page_href)

            page.goto(video_page_href)
            page.wait_for_timeout(1000)
            try:
                show_more_button = page.wait_for_selector("text=Show more", timeout=1500)
                if show_more_button:
                    show_more_button.click()
            except:
                print("No 'Show More' button found.")

            video_page_soup = BeautifulSoup(page.content(),  'html.parser')
            video_description_elem = video_page_soup.select("div.text.site-font-secondary-color")[0]

            if video_title_elem and video_description_elem and video_page_url_elem:
                print('video_title_elem', video_title_elem)
                video_title = video_title_elem.text.strip()
                print('video_title', video_title)

                ## TODO: handle description case where it says show more and contains an array of p tags
                video_description = video_description_elem.text.strip()
                print('video_description', video_description)

                # TODO: inspect get requests to find real href
                # video_download_url = video_page_url_elem["href"]

                # Create a video dictionary
                video_info = {
                    "video_title": video_title,
                    "video_description": video_description,
                    "video_download_url": "",
                }

                # Add the video dictionary to the section_videos list
                section_videos.append(video_info)

        # Add section information to the course_content dictionary
        course_content["section_title"] = section_title
        course_content["section_url"] = section_url
        course_content["section_videos"] = section_videos

        # Close the browser
        browser.close()

        return course_content

if __name__ == "__main__":
    url = "https://tomovhxtv.vhx.tv/browse"  # Replace with the URL of the HTML page
    course_content_dict = extract_course_content(url)

    # Print the course content dictionary
    print(course_content_dict)

