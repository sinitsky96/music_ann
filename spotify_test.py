import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import time
import logging
from keys import client_id, client_secret

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up your credentials

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)

def get_audio_features(track_ids):
    features = []
    for i in range(0, len(track_ids), 100):
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
                time.sleep(5)
        time.sleep(1)
    return features

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
                if offset >= 1000:
                    logging.info("Reached maximum offset limit of 1000. Moving to next query.")
                    break
                break
            except Exception as e:
                logging.error(f"Error searching tracks: {e}")
                retries -= 1
                time.sleep(5)
        time.sleep(1)
    return track_ids[:max_tracks]

def get_top_playlists(query):
    playlists = []
    retries = 3
    while retries > 0:
        try:
            results = sp.search(q=query, type='playlist', limit=10)
            playlists = results['playlists']['items']
            logging.info(f"Retrieved {len(playlists)} playlists for query '{query}'.")
            break
        except Exception as e:
            logging.error(f"Error retrieving playlists: {e}")
            retries -= 1
            time.sleep(5)
    return playlists

def get_tracks_from_playlist(playlist_id):
    track_ids = []
    retries = 3
    while retries > 0:
        try:
            results = sp.playlist_tracks(playlist_id)
            track_ids = [item['track']['id'] for item in results['items'] if item['track'] is not None]
            logging.info(f"Retrieved {len(track_ids)} tracks from playlist {playlist_id}.")
            break
        except Exception as e:
            logging.error(f"Error retrieving tracks from playlist: {e}")
            retries -= 1
            time.sleep(5)
    return track_ids

def process_metal_songs():
    # Collect track IDs using different queries
    queries = [
        "genre:metal", "genre:heavy metal", "genre:death metal", "genre:black metal",
        "genre:thrash metal", "genre:doom metal", "genre:power metal", "genre:folk metal"
    ]
    track_ids = []
    for query in queries:
        track_ids.extend(search_tracks(query, limit=50, max_tracks=100))

    # Get audio features for the collected track IDs
    audio_features = get_audio_features(track_ids[:1000])

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
                        time.sleep(5)

def process_playlists():
    # Get top playlists
    top_playlists = get_top_playlists("top hits")
    
    # Open CSV file for writing
    with open('playlist_songs_features.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'playlist_name', 'track_id', 'track_name', 'artist', 'danceability', 'energy', 'key', 
            'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
            'valence', 'tempo', 'duration_ms', 'time_signature'
        ])
        
        # Process each playlist
        for playlist in top_playlists:
            playlist_name = playlist['name']
            playlist_id = playlist['id']
            track_ids = get_tracks_from_playlist(playlist_id)
            audio_features = get_audio_features(track_ids)
            
            for features in audio_features:
                if features:
                    retries = 3
                    while retries > 0:
                        try:
                            track = sp.track(features['id'])
                            writer.writerow([
                                playlist_name,
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
                            logging.info(f"Written to CSV: {track['name']} by {track['artists'][0]['name']} from playlist {playlist_name}")
                            break
                        except Exception as e:
                            logging.error(f"Error writing to CSV: {e}")
                            retries -= 1
                            time.sleep(5)

def main():
    # Process metal songs
    # process_metal_songs()
    
    # Process playlists
    process_playlists()

if __name__ == "__main__":
    main()
