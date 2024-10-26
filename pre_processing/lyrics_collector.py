import logging
import requests
import re
from bs4 import BeautifulSoup
import os
from keys import genius_access_token

def get_lyrics_genius(song_title, artist_name):
    """
    Get lyrics using Genius API and web scraping
    
    Args:
        song_title (str): The song title
        artist_name (str): The artist name
        
    Returns:
        str: Song lyrics or None if not found
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
                page = requests.get(song_url)
                soup = BeautifulSoup(page.content, 'html.parser')
                
                lyrics_containers = soup.select('div[class*="Lyrics__Container"]')
                if lyrics_containers:
                    lyrics = '\n'.join([container.get_text() for container in lyrics_containers])
                    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
                    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s.strip()])
                    return lyrics.strip()
                
        return None
        
    except Exception as e:
        logging.error(f"Error fetching lyrics: {e}")
        return None
