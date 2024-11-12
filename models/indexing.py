import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SongIndexer:
    def __init__(self, n_components=10):
        """Initialize the SongIndexer with PCA components."""
        self.n_components = n_components
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=self.n_components)
        self.data = None
        self.reduced_data = None
        
    def load_and_preprocess(self, filepath, features):
        """Load and preprocess the data."""
        self.data = pd.read_csv(filepath)
        normalized_data = self.scaler.fit_transform(self.data[features])
        self.reduced_data = self.pca.fit_transform(normalized_data).astype(np.float32)
        return self.reduced_data

    def create_index(self, index_type='FlatL2', num_clusters=100, m=32, n_pq=8, nprobe=10):
        """
        Create a FAISS index based on the specified type and parameters.
        
        Args:
            index_type (str): Type of FAISS index ('FlatL2', 'FlatIP', 'HNSWFlat', 'IVFFlat', 'IVFPQ')
            num_clusters (int): Number of clusters for IVF-based indices
            m (int): Number of connections per node in HNSW
            n_pq (int): Number of product quantizer centroids
            nprobe (int): Number of clusters to visit during search
            
        Returns:
            faiss.Index: The created FAISS index
        """
        if self.reduced_data is None:
            raise ValueError("Data not loaded. Call load_and_preprocess first.")

        dimension = self.reduced_data.shape[1]
        logging.info(f"Creating {index_type} index with dimension {dimension}")

        try:
            if index_type == 'FlatL2':
                index = faiss.IndexFlatL2(dimension)
            
            elif index_type == 'FlatIP':
                index = faiss.IndexFlatIP(dimension)
                # Normalize vectors for cosine similarity
                data_copy = self.reduced_data.copy()
                faiss.normalize_L2(data_copy)
                self.reduced_data = data_copy
            
            elif index_type == 'HNSWFlat':
                index = faiss.IndexHNSWFlat(dimension, m)
                logging.info(f"Created HNSWFlat index with m={m}")
            
            elif index_type == 'IVFFlat':
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, num_clusters, faiss.METRIC_L2)
                index.train(self.reduced_data)
                logging.info(f"Created IVFFlat index with {num_clusters} clusters")
            
            elif index_type == 'IVFPQ':
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFPQ(quantizer, dimension, num_clusters, n_pq, 8)
                index.train(self.reduced_data)
                logging.info(f"Created IVFPQ index with {num_clusters} clusters and {n_pq} PQ centroids")
            
            else:
                raise ValueError(f"Unsupported index type: {index_type}")

            # Add data to index
            index.add(self.reduced_data)
            logging.info(f"Added {len(self.reduced_data)} vectors to index")

            # Set nprobe for applicable indices
            if index_type in ['IVFFlat', 'IVFPQ']:
                index.nprobe = nprobe
                logging.info(f"Set nprobe to {nprobe}")

            return index

        except Exception as e:
            logging.error(f"Error creating index: {str(e)}")
            raise

    def build_playlist(self, index, start_index, playlist_size):
        """
        Build a playlist using the provided index.
        
        Args:
            index (faiss.Index): FAISS index to use for similarity search
            start_index (int): Starting song index
            playlist_size (int): Desired size of the playlist
            
        Returns:
            list: List of song indices forming the playlist
        """
        playlist = [start_index]
        added_indices = set(playlist)
        
        while len(playlist) < playlist_size:
            last_vector = self.reduced_data[playlist[-1]].reshape(1, -1)
            distances, indices = index.search(last_vector, 10)
            
            for idx in indices[0]:
                if idx not in added_indices:
                    playlist.append(int(idx))
                    added_indices.add(idx)
                    break
        
        return playlist

    def get_song_names(self, playlist_indices):
        """Get song names for the given playlist indices."""
        return [self.data.iloc[idx]['name'] for idx in playlist_indices]


def test_indices(filepath, features, start_song_index=0, playlist_size=10):
    """Test function to demonstrate usage."""
    indexer = SongIndexer(n_components=10)
    indexer.load_and_preprocess(filepath, features)
    
    index_configs = {
        "FlatL2": {},
        "FlatIP": {},
        "HNSWFlat": {"m": 32},
        "IVFFlat": {"num_clusters": 100, "nprobe": 10},
        "IVFPQ": {"num_clusters": 100, "n_pq": 8, "nprobe": 10}
    }
    
    results = {}
    for name, config in index_configs.items():
        try:
            logging.info(f"\nTesting {name} index...")
            index = indexer.create_index(index_type=name, **config)
            playlist_indices = indexer.build_playlist(index, start_song_index, playlist_size)
            playlist_songs = indexer.get_song_names(playlist_indices)
            results[name] = playlist_songs
            
            # Print results
            print(f"\nPlaylist using {name} index:")
            for i, song in enumerate(playlist_songs, 1):
                print(f"Song {i}: {song}")
                
        except Exception as e:
            logging.error(f"Error testing {name} index: {str(e)}")
            continue
    
    return results


if __name__ == "__main__":
    # Example usage
    features = [
        'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
        'duration_ms', 'time_signature'
    ]
    
    test_indices('data/rock_songs_features.csv', features)
