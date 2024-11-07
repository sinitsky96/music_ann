import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import faiss
from itertools import product

# Load the dataset
file_path = 'data/rock_songs_features.csv'
data = pd.read_csv(file_path)

# Feature columns to use for similarity calculation
feature_columns = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
    'valence', 'tempo', 'duration_ms', 'time_signature'
]

# Scale the features
scaler = StandardScaler()
normalized_features = scaler.fit_transform(data[feature_columns].values).astype('float32')

# Set up FAISS index for fast similarity searches
d = normalized_features.shape[1]  # Dimensionality of vectors
faiss_index = faiss.IndexFlatIP(d)  # Use cosine similarity
normalized_features = np.ascontiguousarray(normalized_features)

# Normalize for cosine similarity
faiss.normalize_L2(normalized_features)
faiss_index.add(normalized_features)

# Parameters to experiment with
similarity_weights = [(0.5, 0.5), (0.7, 0.3), (0.3, 0.7)]  # (weight to last song, weight to centroid)
feature_weights_options = [
    np.ones(len(feature_columns)),  # Equal weights
    np.array([1.5 if f == 'danceability' else 1 for f in feature_columns]),  # Emphasize danceability
    np.array([1.5 if f == 'energy' else 1 for f in feature_columns])  # Emphasize energy
]
top_k_values = [3, 5, 10]  # Top-K similar songs to consider for selection

# Prepare to save results
results = []

# Function to get the next song based on FAISS similarity search
def get_next_song_faiss(playlist_indices, last_song_idx, centroid, weights, weight_last, weight_centroid, top_k):
    # Calculate weighted similarity to last song
    _, I_last = faiss_index.search(normalized_features[last_song_idx].reshape(1, -1), top_k)
    similarity_to_last = I_last.flatten()


    # Combine similarities with specified weights
    combined_scores = weight_last * similarity_to_last 

    # Exclude songs already in the playlist
    for idx in playlist_indices:
        combined_scores[idx] = -1  # Exclude already selected songs

    # Select the next song with the highest combined similarity
    next_song_idx = np.argmax(combined_scores)
    return next_song_idx

# Function to build a playlist based on parameters
def build_playlist_faiss(initial_idx, playlist_length, weight_last, weight_centroid, feature_weights, top_k):
    playlist_indices = [initial_idx]
    playlist_features = normalized_features[initial_idx].reshape(1, -1)

    for _ in range(playlist_length - 1):
        # If playlist is empty, choose based only on the first song
        centroid = normalized_features[initial_idx]
        
        next_song_idx = get_next_song_faiss(playlist_indices, playlist_indices[-1], centroid, feature_weights, weight_last, weight_centroid, top_k)
        
        playlist_indices.append(next_song_idx)
        playlist_features = np.vstack([playlist_features, normalized_features[next_song_idx]])

    return playlist_indices

# Loop over all parameter combinations and generate playlists
for (weight_last, weight_centroid), feature_weights, top_k in product(similarity_weights, feature_weights_options, top_k_values):
    # Start from the first track for consistency
    initial_idx = 0  # Starting with the first song in the dataset
    playlist_indices = build_playlist_faiss(
        initial_idx=initial_idx, 
        playlist_length=10, 
        weight_last=weight_last, 
        weight_centroid=weight_centroid, 
        feature_weights=feature_weights, 
        top_k=top_k
    )

    # Retrieve playlist song details
    playlist_songs = data.iloc[playlist_indices][['id', 'name', 'artist', 'genre']]
    results.append({
        'weight_last': weight_last,
        'weight_centroid': weight_centroid,
        'feature_weights': feature_weights,
        'top_k': top_k,
        'playlist': playlist_songs
    })

# Display the results for each configuration
for i, result in enumerate(results):
    print(f"\nConfiguration {i+1}:")
    print(f"Similarity weights (Last: {result['weight_last']}, Centroid: {result['weight_centroid']})")
    print(f"Feature Weights: {result['feature_weights']}")
    print(f"Top-K: {result['top_k']}")
    print(result['playlist'])
