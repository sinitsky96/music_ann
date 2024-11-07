import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import time
import logging
from keys import client_id, client_secret
from constants import GENRE_MAP, SUBJECTS
from lyrics_collector import get_lyrics_genius

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Spotify credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)



def get_audio_features(track_ids):
    """
    Retrieve audio features for a list of track IDs from Spotify API.
    
    Args:
        track_ids (list): A list of track IDs.
        
    Returns:
        list: A list of audio features.
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

    Args:
        query (str): The query string to search for.
        limit (int): The number of tracks to retrieve.
        max_tracks (int): Maximum number of tracks to retrieve.
        
    Returns:
        list: A list of track IDs.
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

    Args:
        query (str): The query string to search for.
        limit (int): The number of playlists to retrieve.
        
    Returns:
        list: A list of playlists.
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
    Retrieve track IDs from a Spotify playlist (limited to 30 tracks).

    Args:
        playlist_id (str): The ID of the playlist to retrieve tracks from.
        
    Returns:
        list: A list of track IDs (max 30).
    """
    track_ids = []
    retries = 3
    while retries > 0:
        try:
            results = sp.playlist_tracks(playlist_id, limit=30)
            track_ids = [item['track']['id'] for item in results['items'] if item['track'] is not None]
            logging.info(f"Retrieved {len(track_ids)} tracks from playlist {playlist_id}.")
            break
        except Exception as e:
            logging.error(f"Error retrieving tracks from playlist: {e}")
            retries -= 1
            time.sleep(5)
    return track_ids[:30]

def process_genre_songs(genre_key, max_tracks=100):
    """
    Process songs for a specific genre and its subgenres.

    Args:
        genre_key (str): The key for the genre to process.
        max_tracks (int): Maximum number of tracks to process for the genre.
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
            'valence', 'tempo', 'duration_ms', 'time_signature', 'subject', 'language', 
            'release_date', 'popularity'
        ])
        
        for features in audio_features:
            if features:
                retries = 3
                while retries > 0:
                    try:
                        track = sp.track(features['id'])
                        language, release_date, subject = get_lyrics_genius(track['name'], track['artists'][0]['name'], SUBJECTS)
                        
                        # Skip if no lyrics found
                        if subject is None:
                            logging.info(f"Skipping {track['name']} by {track['artists'][0]['name']} - No lyrics found")
                            break
                        
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
                            subject,
                            language,
                            release_date,
                            track['popularity']
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

    Args:
        playlist_type (str): Type of playlist to process.
        limit (int): Number of playlists to process.
    """
    top_playlists = get_top_playlists(playlist_type, limit=limit)
    
    with open('data/playlist_songs_features.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'playlist_name', 'track_id', 'track_name', 'artist', 'genre', 'danceability', 
            'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 
            'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 
            'time_signature', 'subject', 'language', 'release_date', 'popularity'
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
                            artist_id = track['artists'][0]['id']
                            artist = sp.artist(artist_id)
                            genres = artist['genres'][0] if artist['genres'] else 'unknown'
                            language, release_date, subject = get_lyrics_genius(track['name'], track['artists'][0]['name'], SUBJECTS)
                            
                            # Skip if no lyrics found
                            if subject is None:
                                logging.info(f"Skipping {track['name']} by {track['artists'][0]['name']} - No subject found")
                                break
                            
                            writer.writerow([
                                playlist_name,
                                features['id'],
                                track['name'],
                                track['artists'][0]['name'],
                                genres,
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
                                subject,
                                language,
                                release_date,
                                track['popularity']
                            ])
                            logging.info(f"Written to CSV: {track['name']} by {track['artists'][0]['name']} ({genres}) from playlist {playlist_name}")
                            break
                        except Exception as e:
                            logging.error(f"Error writing to CSV: {e}")
                            retries -= 1
                            time.sleep(5)

def process_genre_list(genre_list=None, max_tracks=100):
    """
    Process songs for a list of genres.

    Args:
        genre_list (list): List of genres to process. If None, all genres in GENRE_MAP will be processed.
        max_tracks (int): Maximum number of tracks to process for each genre.
    """
    if genre_list is None:
        genre_list = list(GENRE_MAP.keys())
    
    for genre in genre_list:
        logging.info(f"Processing {genre} songs...")
        process_genre_songs(genre, max_tracks=max_tracks)

def main():
    """
    Main execution function that processes specified genres and optionally playlists.
    """
    # Process genres
    # process_genre_list(genre_list=['metal', 'rock', 'electronic'], max_tracks=100)
    
    # Process playlists 
    process_playlists(playlist_type="top hits", limit=10)

if __name__ == "__main__":
    main()
