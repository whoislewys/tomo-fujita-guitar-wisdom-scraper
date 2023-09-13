# Tomo Fujita Guitar Wisdom Scraper
I just bought the Tomo Fujita Guitar Wisdom course, but I'm going to Guatemala and the internet isn't good for streaming 1080p 60fps internet. So I wrote a scraper!

2 part scraper
1. Scrapes all course video pages & metadata into a JSON file
2. Read page urls from the JSON file to actually download the videos

This was astonishingly fast to write thanks to playwright & mostly GPT4

## Setup
Install deps
```
python3.11 -m venv scrape_env
source scrape_env/bin/activate
pip install -r requirements.txt
```

## Running
To scrape together a json file of all the course pages & metadata, run
```
python3 course_content.json
```
making sure to sign in after the browser window opens

To scrape the videos URLs, modify `download_files_from_extracted_json.py` with the json file of the sections you want to scrape videos from and run (for example, the generated `course_content.json` from above. or you can cut and paste sections you don't want from that big one into smaller json file) and run:
```
python3 course_content.json
```

Again, making sure to sign in when the browser opens.

If you get an error, it's likely due to being signed in on too many devices. The course UI will ask you to sign out all other sessions except for the current one. Do that and everything should continue working normally!

