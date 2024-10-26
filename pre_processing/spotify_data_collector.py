import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import time
import logging
from keys import client_id, client_secret
from constants import GENRE_MAP
from lyrics_collector import get_lyrics_genius

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Spotify credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)



def get_audio_features(track_ids):
    """
    Retrieve audio features for a list of track IDs from Spotify API.
    """
    features = []
    for i in range(0, len(track_ids), 100):
        retries = 3
        while retries > 0:
            try:
                audio_features = sp.audio_features(track_ids[i:i+100])
                features.extend(audio_features)
                break
            except Exception as e:
                logging.error(f"Error retrieving audio features: {e}")
                retries -= 1
                time.sleep(5)
        time.sleep(1)
    return features

def search_tracks(query, limit, max_tracks):
    """
    Search for tracks on Spotify using a query string.
    """
    track_ids = []
    offset = 0
    genre_name = query.split(':')[1] if ':' in query else query
    
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
                logging.info(f"Collected {len(track_ids)} track IDs so far for {genre_name}.")
                if offset >= 1000:
                    logging.info(f"Reached maximum offset limit of 1000 for {genre_name}. Moving to next query.")
                    break
                break
            except Exception as e:
                logging.error(f"Error searching tracks for {genre_name}: {e}")
                retries -= 1
                time.sleep(5)
        time.sleep(1)
    return track_ids[:max_tracks]

def get_top_playlists(query, limit=10):
    """
    Search for top playlists on Spotify using a query string.
    """
    playlists = []
    retries = 3
    while retries > 0:
        try:
            results = sp.search(q=query, type='playlist', limit=limit)
            playlists = results['playlists']['items']
            logging.info(f"Retrieved {len(playlists)} playlists for query '{query}'.")
            break
        except Exception as e:
            logging.error(f"Error retrieving playlists: {e}")
            retries -= 1
            time.sleep(5)
    return playlists

def get_tracks_from_playlist(playlist_id):
    """
    Retrieve all track IDs from a Spotify playlist.
    """
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

def process_genre_songs(genre_key, max_tracks=100):
    """
    Process songs for a specific genre and its subgenres.
    """
    if genre_key not in GENRE_MAP:
        logging.error(f"Genre '{genre_key}' not found in GENRE_MAP")
        return

    track_ids = []
    for subgenre in GENRE_MAP[genre_key]:
        query = f"genre:{subgenre}"
        track_ids.extend(search_tracks(query, limit=50, max_tracks=max_tracks))

    audio_features = get_audio_features(track_ids[:max_tracks*len(GENRE_MAP[genre_key])])

    output_file = f'data/{genre_key}_songs_features.csv'
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'id', 'name', 'artist', 'genre', 'danceability', 'energy', 'key', 'loudness', 
            'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
            'valence', 'tempo', 'duration_ms', 'time_signature', 'lyrics'
        ])
        
        for features in audio_features:
            if features:
                retries = 3
                while retries > 0:
                    try:
                        track = sp.track(features['id'])
                        lyrics = get_lyrics_genius(track['name'], track['artists'][0]['name'])
                        
                        writer.writerow([
                            features['id'],
                            track['name'],
                            track['artists'][0]['name'],
                            genre_key,
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
                            features['time_signature'],
                            lyrics
                        ])
                        logging.info(f"Written to CSV: {track['name']} by {track['artists'][0]['name']}")
                        break
                    except Exception as e:
                        logging.error(f"Error writing to CSV: {e}")
                        retries -= 1
                        time.sleep(5)

def process_playlists(playlist_type="top hits", limit=10):
    """
    Process top playlists, collecting audio features for their tracks.
    """
    top_playlists = get_top_playlists(playlist_type, limit=limit)
    
    with open('data/playlist_songs_features.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'playlist_name', 'track_id', 'track_name', 'artist', 'danceability', 'energy', 'key', 
            'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
            'valence', 'tempo', 'duration_ms', 'time_signature', 'lyrics'
        ])
        
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
                            lyrics = get_lyrics_genius(track['name'], track['artists'][0]['name'])
                            
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
                                features['time_signature'],
                                lyrics  
                            ])
                            logging.info(f"Written to CSV: {track['name']} by {track['artists'][0]['name']} from playlist {playlist_name}")
                            break
                        except Exception as e:
                            logging.error(f"Error writing to CSV: {e}")
                            retries -= 1
                            time.sleep(5)

def main():
    """
    Main execution function that processes specified genres and optionally playlists.
    """
    # genres_to_process = ['metal', 'rock', 'electronic']
    # for genre in genres_to_process:
    #     logging.info(f"Processing {genre} songs...")
    #     process_genre_songs(genre, max_tracks=100)
    
    # Process playlists
    process_playlists(playlist_type="top hits", limit=10)

if __name__ == "__main__":
    main()