import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

data = pd.read_csv('metal_songs_features.csv')

features = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature'
]

scaler = StandardScaler()
normalized_data = scaler.fit_transform(data[features])

pca = PCA(n_components=10)
reduced_data = pca.fit_transform(normalized_data).astype(np.float32)

dimension = reduced_data.shape[1]
num_clusters = 100
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, num_clusters, faiss.METRIC_L2)

index.train(reduced_data)

index.add(reduced_data)

index.nprobe = 10


def build_playlist(data, start_index, playlist_size):
    """Build a playlist by iteratively finding the closest song to the last added song."""
    playlist = [start_index]
    added_indices = set(playlist)

    while len(playlist) < playlist_size:
        # Get the vector of the last added song
        last_song_vector = reduced_data[playlist[-1]].reshape(1, -1)

        # Perform the search to find the closest songs
        distances, indices = index.search(last_song_vector, 10)

        # Find the closest song not already in the playlist
        for idx in indices[0]:
            if idx not in added_indices:
                playlist.append(idx)
                added_indices.add(idx)
                break

    # Print the playlist
    print("\nGenerated Playlist:")
    for i, song_idx in enumerate(playlist):
        song_data = data.iloc[song_idx][['name']].to_dict()
        print(f"Song {i + 1}: {song_data}")


start_song_index = 0
desired_playlist_size = 10

build_playlist(data, start_song_index, desired_playlist_size)
