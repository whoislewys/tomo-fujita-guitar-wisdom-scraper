import os
import requests
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
  browser = p.chromium.launch(headless=False)
  page = browser.new_page()
  page.goto("https://tomovhxtv.vhx.tv/browse")
  # Sleep for 30 seconds to let me sign in / login
  page.wait_for_timeout(30 * 1000)

  # Define the path to your JSON file
  # json_file_path = "course_content.json"
  json_file_path = "section-1.json"
  # Read the JSON data from the file
  with open(json_file_path, "r") as json_file:
      data = json.load(json_file)

  # Set the base directory for course downloads
  base_download_dir = "./course_downloads"

  # Iterate over each section in the JSON
  for section in data:
      section_index = section["section_index"]
      section_title = section["section_title"]
      section_dir = os.path.join(base_download_dir, f"{section_index}_{section_title}")

      # Create a directory for the section if it doesn't exist
      os.makedirs(section_dir, exist_ok=True)

      # Iterate over each section video
      for video in section["section_videos"]:
          video_page_url = video["video_page_url"]
          video_page_url_responses = []
          # Subscribe to "response" events. This will allow us to scrape the download URL from the current video page
          page.on("response", lambda response: video_page_url_responses.append(response))
          page.goto(video_page_url)
          page.wait_for_timeout(10_000) # wait for quite a bit to ensure we get back the response containing the download url.

          # Inspect get requests to find vimeo request and scrape download link
          requestURLSearchString = 'player.vimeo.com/video'
          matching_response = None
          for response in video_page_url_responses:
              # print('video_page_url_responses: ', response)
              if requestURLSearchString in response.url:
                  matching_response = response
                  break
          print('video response: ', matching_response)
          video_download_url = ''
          if matching_response is not None:
              response_json = matching_response.json()
              # print('response_json: ', response_json)
              # get the URL for the 720p video. its 60FPS, but smaller than 1080p.
              progressive_json_section = response_json['request']['files']['progressive']
              # print('progressive_json_section: ', progressive_json_section)
              for item in progressive_json_section:
                  # print('item [width]: ', item['width'])
                  if item['width'] == 1280 and item['height'] == 720:
                      video_download_url = item['url']
                      # print('video_download_url',video_download_url)
                      break

          video_index = video["video_index"]
          video_title = video["video_title"]

          # Generate the video filename
          video_filename = f"{video_index}_{video_title}.mp4"

          # Download the video and save it to the section directory
          print(f'Downloading {video_filename} at url: {video_download_url}...')
          response = requests.get(video_download_url)
          if response.status_code == 200:
              video_path = os.path.join(section_dir, video_filename)
              with open(video_path, "wb") as video_file:
                  video_file.write(response.content)
              print(f"Downloaded: {video_path}")
          else:
              print(f"Failed to download: {video_filename}")

  print("Download completed.")

