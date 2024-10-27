import logging
import requests
import re
from bs4 import BeautifulSoup
import os
from keys import genius_access_token

def get_lyrics_genius(song_title, artist_name):
    """
    Get lyrics, language, and release date using Genius API and web scraping
    
    Args:
        song_title (str): The song title
        artist_name (str): The artist name
        
    Returns:
        tuple: (lyrics, language, release_date) or (None, None, None) if not found
    """
    base_url = 'https://api.genius.com'
    headers = {'Authorization': f'Bearer {genius_access_token}'}
    search_url = f"{base_url}/search"
    
    params = {
        'q': f"{song_title} {artist_name}"
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        json_data = response.json()
        
        for hit in json_data['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_url = hit['result']['url']
                
                # Get song details to extract language and release date
                song_api_path = hit['result']['api_path']
                song_response = requests.get(f"{base_url}{song_api_path}", headers=headers)
                song_data = song_response.json()
                language = song_data['response']['song'].get('language', 'unknown')
                release_date = song_data['response']['song'].get('release_date', 'unknown')
                
                # Get lyrics from webpage
                page = requests.get(song_url)
                soup = BeautifulSoup(page.content, 'html.parser')
                
                lyrics_containers = soup.select('div[class*="Lyrics__Container"]')
                if lyrics_containers:
                    lyrics = '\n'.join([container.get_text() for container in lyrics_containers])
                    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
                    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s.strip()])
                    return lyrics.strip(), language, release_date
                
        return None, None, None
        
    except Exception as e:
        logging.error(f"Error fetching lyrics: {e}")
        return None, None, None
