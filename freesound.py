import requests
import os
import time
import re

# Your Freesound API key
API_KEY = "9cp9J7NnbQCaTnP2wiGPOp0wjHZ1Jts1yb2lDHGt"

# Base URL for the Freesound API
BASE_URL = "https://freesound.org/apiv2"

# Example: Search for sounds
def search_sounds(page=1, page_size=15):
    endpoint = f"{BASE_URL}/search/text/"
    params = {
        "page": page,
        "page_size": page_size,
        "fields": "id,name,url",
        "token": API_KEY,
    }
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def sanitize_filename(filename):
    # Remove any characters that are not alphanumeric, spaces, hyphens, or underscores
    return re.sub(r'[^a-zA-Z0-9 \-_]', '', filename).strip()

def download_sound(sound_id, download_dir):
    # Construct the sound instance endpoint
    endpoint = f"{BASE_URL}/sounds/{sound_id}/"
    params = {"token": API_KEY}
    
    # Get sound instance details
    response = requests.get(endpoint, params=params)
    if response.status_code != 200:
        print(f"Error getting sound details: {response.status_code}")
        return None
    
    sound_data = response.json()
    download_url = sound_data['previews']['preview-hq-mp3']
    filename = f"{sound_id}_{sound_data['name']}.mp3"
    safe_filename = sanitize_filename(filename) + ".mp3"
    
    # Download the file
    audio_response = requests.get(download_url)
    if audio_response.status_code != 200:
        print(f"Error downloading audio: {audio_response.status_code}")
        return None
    
    # Save the file
    file_path = os.path.join(download_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(audio_response.content)
    
    return file_path

def download_all_sounds(max_sounds=1000000000000000):
    download_dir = "downloaded_sounds"
    os.makedirs(download_dir, exist_ok=True)
    
    page = 1
    downloaded_count = 0
    
    while downloaded_count < max_sounds:
        results = search_sounds(page=page, page_size=15)
        if not results or not results['results']:
            break
        
        for sound in results['results']:
            if downloaded_count >= max_sounds:
                break
            
            print(f"Downloading: ID: {sound['id']}, Name: {sound['name']}")
            file_path = download_sound(sound['id'], download_dir)
            if file_path:
                print(f"Downloaded to: {file_path}")
                downloaded_count += 1
            
            # Be nice to the API by adding a small delay between requests
            time.sleep(1)
        
        page += 1
    
    print(f"Downloaded {downloaded_count} sounds.")

# Example usage
if __name__ == "__main__":
    download_all_sounds()