from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import requests
import openpyxl
import json

# Set your YouTube API key
api_key = 'AIzaSyBCrt49j0ilELtPmu-COGfvk0ha_R7ui7Q'

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

# Search for videos based on a keyword
def search_videos(keyword, max_results=20):
    request = youtube.search().list(
        q=keyword,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    return response.get('items', [])

# Get channel details including email and social media links
def get_channel_details(channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    return response.get('items', [])

# Fetch additional information from the web if not available on YouTube
def fetch_additional_info(channel_url):
    response = requests.get(channel_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Example: Extract email and social media links (needs customization)
    return {
        'email': 'example@example.com',  # Placeholder example
        'facebook': 'https://facebook.com/example',  # Placeholder example
        # Add other fields as needed
    }

# Save data in Excel format
def save_to_excel(data, filename='output.xlsx'):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Video Title', 'Channel Name', 'Email', 'Facebook', 'Instagram', 'WhatsApp'])
    for item in data:
        ws.append([
            item['video_title'], 
            item['channel_name'], 
            item['email'], 
            item['facebook'], 
            item['instagram'], 
            item['whatsapp']
        ])
    wb.save(filename)

# Save data in JSON format
def save_to_json(data, filename='output.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Main function to run the scraper
def main():
    keyword = 'gaming'  # Example keyword
    videos = search_videos(keyword)

    data = []
    for video in videos:
        video_title = video['snippet']['title']
        channel_id = video['snippet']['channelId']
        channel_title = video['snippet']['channelTitle']

        # Get channel details from YouTube
        channel_details = get_channel_details(channel_id)
        if channel_details:
            channel_info = channel_details[0]
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            additional_info = fetch_additional_info(channel_url)
            
            data.append({
                'video_title': video_title,
                'channel_name': channel_title,
                'email': additional_info.get('email', 'N/A'),
                'facebook': additional_info.get('facebook', 'N/A'),
                'instagram': additional_info.get('instagram', 'N/A'),
                'whatsapp': additional_info.get('whatsapp', 'N/A'),
            })
    
    # Save the collected data in the desired format
    save_to_excel(data)
    save_to_json(data)

# Entry point of the script
if __name__ == "__main__":
    main()
