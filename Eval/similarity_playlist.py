import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def load_data(filepath):
    """Load the dataset from a CSV file."""
    return pd.read_csv(filepath)


def preprocess_data(data, features):
    """Normalize the selected features using StandardScaler."""
    scaler = StandardScaler()
    return scaler.fit_transform(data[features])


def apply_pca(data, n_components=10):
    """Reduce data dimensionality using PCA."""
    pca = PCA(n_components=n_components)
    return pca.fit_transform(data).astype(np.float32)


def create_faiss_index(data, num_clusters=100, nprobe=10):
    """Create and train a FAISS index with specified parameters."""
    dimension = data.shape[1]
    quantizer = faiss.IndexFlatL2(dimension)
    index = faiss.IndexIVFFlat(
        quantizer, dimension, num_clusters, faiss.METRIC_L2)
    index.train(data)
    index.add(data)
    index.nprobe = nprobe
    return index


def build_playlist(reduced_data, index, start_index, playlist_size):
    """Build a playlist by finding the closest song iteratively."""
    playlist = [start_index]
    added_indices = set(playlist)

    while len(playlist) < playlist_size:
        last_vector = reduced_data[playlist[-1]].reshape(1, -1)
        distances, indices = index.search(last_vector, 10)

        for idx in indices[0]:
            if idx not in added_indices:
                playlist.append(idx)
                added_indices.add(idx)
                break
    return playlist


def calculate_centroid_distance(reduced_data, playlist1, playlist2):
    """Calculate the centroid distance between two playlists."""
    centroid1 = reduced_data[playlist1].mean(axis=0)
    centroid2 = reduced_data[playlist2].mean(axis=0)
    return np.linalg.norm(centroid1 - centroid2)


def calculate_cosine_similarity(reduced_data, playlist1, playlist2):
    """Calculate cosine similarity between two playlist centroids."""
    centroid1 = reduced_data[playlist1].mean(axis=0).reshape(1, -1)
    centroid2 = reduced_data[playlist2].mean(axis=0).reshape(1, -1)
    return np.dot(centroid1, centroid2.T) / (np.linalg.norm(centroid1) * np.linalg.norm(centroid2))


def calculate_average_pairwise_distance(reduced_data, playlist1, playlist2):
    """Calculate average pairwise distance between songs in two playlists."""
    distances = [
        np.linalg.norm(reduced_data[playlist1[i]] - reduced_data[playlist2[j]])
        for i in range(len(playlist1)) for j in range(i + 1, len(playlist2))
    ]
    return np.mean(distances)


def main():
    filepath = 'data/metal_songs_features.csv'
    features = [
        'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
        'duration_ms', 'time_signature'
    ]
    playlist_size = 10

    # Load and preprocess data
    data = load_data(filepath)
    normalized_data = preprocess_data(data, features)
    reduced_data = apply_pca(normalized_data)

    # Create FAISS index
    index = create_faiss_index(reduced_data)

    # Generate playlists
    start_index1 = np.random.randint(0, len(data))
    start_index2 = np.random.randint(0, len(data))
    playlist1 = build_playlist(
        reduced_data, index, start_index1, playlist_size)
    playlist2 = build_playlist(
        reduced_data, index, start_index2, playlist_size)

    # Calculate and print metrics
    centroid_distance = calculate_centroid_distance(
        reduced_data, playlist1, playlist2)
    print("Centroid distance between the playlists:", centroid_distance)

    cosine_similarity = calculate_cosine_similarity(
        reduced_data, playlist1, playlist2)
    print("Cosine similarity between the playlists:", cosine_similarity[0][0])

    avg_pairwise_distance = calculate_average_pairwise_distance(
        reduced_data, playlist1, playlist2)
    print("Average pairwise distance between the playlists:", avg_pairwise_distance)


if __name__ == "__main__":
    main()
