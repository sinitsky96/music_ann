import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up your credentials
client_id = "a0de4ef556484f7a9b51e9b488cba4a6"
client_secret = "ca78d4aae709437fb9854512080700eb"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)

# Function to get audio features for a list of track IDs
def get_audio_features(track_ids):
    features = []
    for i in range(0, len(track_ids), 100):  # Spotify API allows max 100 track IDs per request
        retries = 3
        while retries > 0:
            try:
                audio_features = sp.audio_features(track_ids[i:i+100])
                features.extend(audio_features)
                logging.info(f"Retrieved audio features for {len(audio_features)} tracks.")
                break
            except Exception as e:
                logging.error(f"Error retrieving audio features: {e}")
                retries -= 1
                time.sleep(5)  # Wait before retrying
        time.sleep(1)  # Delay to avoid hitting rate limits
    return features

# Function to search for tracks with different queries
def search_tracks(query, limit, max_tracks):
    track_ids = []
    offset = 0
    while len(track_ids) < max_tracks:
        retries = 3
        while retries > 0:
            try:
                results = sp.search(q=query, type='track', limit=limit, offset=offset)
                items = results['tracks']['items']
                if not items:
                    break
                track_ids.extend([item['id'] for item in items])
                offset += limit
                logging.info(f"Collected {len(track_ids)} track IDs so far.")
                if offset >= 1000:  # Ensure offset does not exceed 1000
                    logging.info("Reached maximum offset limit of 1000. Moving to next query.")
                    break
                break
            except Exception as e:
                logging.error(f"Error searching tracks: {e}")
                retries -= 1
                time.sleep(5)  # Wait before retrying
        time.sleep(1)  # Delay to avoid hitting rate limits
    return track_ids[:max_tracks]

# Collect track IDs using different queries
queries = [
    "genre:metal", "genre:heavy metal", "genre:death metal", "genre:black metal",
    "genre:thrash metal", "genre:doom metal", "genre:power metal", "genre:folk metal"
]
track_ids = []
for query in queries:
    track_ids.extend(search_tracks(query, limit=50, max_tracks=100))  # Adjust max_tracks to collect up to 100 tracks

# Get audio features for the collected track IDs
audio_features = get_audio_features(track_ids[:100])  # Ensure only 100 tracks are processed

# Write the audio features to a CSV file
with open('metal_songs_features.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        'id', 'name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 
        'time_signature'
    ])
    for features in audio_features:
        if features:
            retries = 3
            while retries > 0:
                try:
                    track = sp.track(features['id'])
                    writer.writerow([
                        features['id'],
                        track['name'],
                        track['artists'][0]['name'],
                        features['danceability'],
                        features['energy'],
                        features['key'],
                        features['loudness'],
                        features['mode'],
                        features['speechiness'],
                        features['acousticness'],
                        features['instrumentalness'],
                        features['liveness'],
                        features['valence'],
                        features['tempo'],
                        features['duration_ms'],
                        features['time_signature']
                    ])
                    logging.info(f"Written to CSV: {track['name']} by {track['artists'][0]['name']}")
                    break
                except Exception as e:
                    logging.error(f"Error writing to CSV: {e}")
                    retries -= 1
                    time.sleep(5)  # Wait before retrying
