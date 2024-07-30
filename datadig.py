from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# Your YouTube API key
YOUTUBE_API_KEY = 'AIzaSyBCrt49j0ilELtPmu-COGfvk0ha_R7ui7Q'

# Setup YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Setup Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
service = Service('C:/Users/dewan/data scrapping/datadig/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

def fetch_video_data(keyword):
    videos = []
    next_page_token = None
    
    while True:
        request = youtube.search().list(
            q=keyword,
            part='snippet',
            type='video',
            maxResults=50,  # Maximum per request
            pageToken=next_page_token
        )
        response = request.execute()
        
        videos.extend(response['items'])
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token or len(videos) >= 500:
            break
    
    return videos

def fetch_channel_info(channel_id):
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    response = request.execute()
    channel_info = response['items'][0]
    return {
        'title': channel_info['snippet']['title'],
        'subscriber_count': channel_info['statistics'].get('subscriberCount', 'N/A')
    }

def fetch_additional_info(channel_url):
    try:
        driver.get(channel_url)
        
        # Wait for the "About" section to be fully loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-channel-about-metadata-renderer'))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract email
        email_element = soup.find('a', href=lambda href: href and 'mailto:' in href)
        email = email_element.get('href', '').replace('mailto:', '') if email_element else 'N/A'
        
        # Extract social media links
        facebook_element = soup.find('a', href=lambda href: 'facebook.com' in href)
        facebook = facebook_element.get('href', 'N/A') if facebook_element else 'N/A'
        
        instagram_element = soup.find('a', href=lambda href: 'instagram.com' in href)
        instagram = instagram_element.get('href', 'N/A') if instagram_element else 'N/A'
        
        return {
            'email': email,
            'facebook': facebook,
            'instagram': instagram,
        }
    except Exception as e:
        print(f"Error fetching additional info: {e}")
        return {
            'email': 'N/A',
            'facebook': 'N/A',
            'instagram': 'N/A',
        }

def main(keyword):
    video_data = fetch_video_data(keyword)
    
    results = []
    
    for video in video_data:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        channel_id = video['snippet']['channelId']
        channel_info = fetch_channel_info(channel_id)
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        additional_info = fetch_additional_info(channel_url)
        
        results.append({
            'video_id': video_id,
            'video_title': video_title,
            'channel_id': channel_id,
            'channel_title': channel_info['title'],
            'subscriber_count': channel_info['subscriber_count'],
            'channel_url': channel_url,
            'email': additional_info['email'],
            'facebook': additional_info['facebook'],
            'instagram': additional_info['instagram'],
        })
    
    # Save results to Excel
    df = pd.DataFrame(results)
    df.to_excel('youtube_data.xlsx', index=False)
    
    # Save results to JSON
    df.to_json('youtube_data.json', orient='records')

if __name__ == "__main__":
    keyword = input("Enter a keyword to search on YouTube: ")
    main(keyword)
    driver.quit()
