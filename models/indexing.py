import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load and preprocess data
data = pd.read_csv('data/metal_songs_features.csv')
features = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature'
]
scaler = StandardScaler()
normalized_data = scaler.fit_transform(data[features])

# Reduce dimensions with PCA
pca = PCA(n_components=10)
reduced_data = pca.fit_transform(normalized_data).astype(np.float32)

# Indexing methods to test
index_methods = {
    "FlatL2": faiss.IndexFlatL2(reduced_data.shape[1]),
    "FlatIP": faiss.IndexFlatIP(reduced_data.shape[1]),
    # "IVFFlat": faiss.IndexIVFFlat(faiss.IndexFlatL2(reduced_data.shape[1]), reduced_data.shape[1]),
    # "IVFPQ": faiss.IndexIVFPQ(faiss.IndexFlatL2(reduced_data.shape[1]), reduced_data.shape[1],subquantizers=8, bits=8),
    "HNSWFlat": faiss.IndexHNSWFlat(reduced_data.shape[1], 32)
}

# Trainable indices need training
for name, index in index_methods.items():
    if isinstance(index, faiss.IndexIVFFlat) or isinstance(index, faiss.IndexIVFPQ):
        index.train(reduced_data)

# Normalize for cosine similarity in FlatIP
if "FlatIP" in index_methods:
    faiss.normalize_L2(reduced_data)

# Add data to each index
for index in index_methods.values():
    index.add(reduced_data)

# Playlist generation function
def build_playlist(data, index, start_index, playlist_size):
    """Build a playlist by iteratively finding the closest song to the last added song."""
    playlist = [start_index]
    added_indices = set(playlist)
    
    while len(playlist) < playlist_size:
        last_song_vector = reduced_data[playlist[-1]].reshape(1, -1)
        distances, indices = index.search(last_song_vector, 10)
        
        for idx in indices[0]:
            if idx not in added_indices:
                playlist.append(idx)
                added_indices.add(idx)
                break
                
    return [data.iloc[song_idx]['name'] for song_idx in playlist]

# Test each index and store the resulting playlists
playlists_by_index = {}
start_song_index = 0
desired_playlist_size = 10

for name, index in index_methods.items():
    print(f"\nGenerating playlist with {name} index...")
    playlist = build_playlist(data, index, start_song_index, desired_playlist_size)
    playlists_by_index[name] = playlist

# Display playlists
for name, playlist in playlists_by_index.items():
    print(f"\nPlaylist using {name} index:")
    for i, song in enumerate(playlist, 1):
        print(f"Song {i}: {song}")
