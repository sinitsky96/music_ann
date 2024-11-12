import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import optuna
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from models.indexing import SongIndexer

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'optuna_logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Generate timestamp for unique log files
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(LOGS_DIR, f'optuna_optimization_{timestamp}.log')
results_file = os.path.join(LOGS_DIR, f'optimization_results_{timestamp}.txt')
study_db = os.path.join(LOGS_DIR, f'optuna_study_{timestamp}.db')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Log the start of the optimization
logging.info(f"Starting optimization. Logs will be saved to: {log_file}")

# Define available FAISS index types
FAISS_INDEX_TYPES = [
    'FlatL2',
    'FlatIP',
    'HNSWFlat',
    'IVFFlat',
    'IVFPQ'
]

def calculate_playlist_similarity(indexer, playlist1, playlist2):
    """
    Calculate similarity between two playlists using cosine similarity of their vectors.
    
    Args:
        indexer (SongIndexer): The indexer containing the reduced data
        playlist1 (list): First playlist indices
        playlist2 (list): Second playlist indices
        
    Returns:
        float: Similarity score between the playlists
    """
    # Get vectors for both playlists
    vectors1 = indexer.reduced_data[playlist1]
    vectors2 = indexer.reduced_data[playlist2]
    
    # Calculate centroid for each playlist
    centroid1 = np.mean(vectors1, axis=0).reshape(1, -1)
    centroid2 = np.mean(vectors2, axis=0).reshape(1, -1)
    
    # Calculate cosine similarity between centroids
    similarity = cosine_similarity(centroid1, centroid2)[0][0]
    
    return similarity

def objective(trial):
    """
    Objective function for Optuna optimization.
    """
    # Define features first to know the maximum possible components
    features = [
        'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
        'duration_ms', 'time_signature'
    ]
    
    # Calculate max components based on number of features
    max_components = len(features)
    max_components = (max_components // 8) * 8
    
    # First suggest n_components and ensure it's compatible with PQ
    n_components = trial.suggest_int('n_components', 8, max_components, step=8)
    index_type = trial.suggest_categorical('index_type', FAISS_INDEX_TYPES)
    
    # Initialize SongIndexer
    indexer = SongIndexer(n_components=n_components)
    
    try:
        filepath = 'data/rock_songs_features.csv'
        reduced_data = indexer.load_and_preprocess(filepath, features)
        logging.info(f"Data preprocessed with {n_components} components")
        
        # Calculate appropriate number of clusters based on dataset size
        n_data_points = len(indexer.data)
        
        # FAISS requires at least 39 training points per cluster
        # For IVFPQ, we also need to consider the PQ centroids (256 by default)
        min_clusters = 4
        max_clusters = min(
            n_data_points // 39,  # Ensure enough training points per cluster
            int(np.sqrt(n_data_points)),  # Keep clusters reasonable for dataset size
            32  # Set an upper limit to avoid training issues
        )
        
        logging.info(f"Dataset size: {n_data_points}, cluster range: [{min_clusters}, {max_clusters}]")
        
    except Exception as e:
        logging.error(f"Data preprocessing failed: {str(e)}")
        return float('inf')
    
    # Define index-specific parameters
    index_params = {
        'index_type': index_type,
        'nprobe': trial.suggest_int('nprobe', 1, max(2, max_clusters))  # Adjust nprobe range
    }
    
    # Add conditional parameters based on index type
    if index_type in ['IVFFlat', 'IVFPQ']:
        index_params['num_clusters'] = trial.suggest_int('num_clusters', min_clusters, max_clusters)
    
    if index_type == 'HNSWFlat':
        index_params['m'] = trial.suggest_int('m', 16, 64)
    
    if index_type == 'IVFPQ':
        # For small datasets, use smaller PQ sizes
        if n_data_points < 1000:
            possible_n_pq = [4, 8]  # Smaller PQ sizes for small datasets
        else:
            possible_n_pq = [8, 16]
        
        possible_n_pq = [n for n in possible_n_pq if n_components % n == 0]
        if possible_n_pq:
            index_params['n_pq'] = trial.suggest_categorical('n_pq', possible_n_pq)
        else:
            return float('-inf')  # Skip invalid configurations
    
    # Create FAISS index
    try:
        index = indexer.create_index(**index_params)
        logging.info(f"Created {index_type} index with parameters: {index_params}")
    except Exception as e:
        logging.error(f"Index creation failed: {str(e)}")
        return float('inf')
    
    # Generate multiple playlist pairs and average their similarities
    n_pairs = 5
    playlist_size = 10
    total_similarity = 0.0
    
    try:
        for _ in range(n_pairs):
            # Generate random start indices
            start_index1 = np.random.randint(0, len(indexer.data))
            start_index2 = np.random.randint(0, len(indexer.data))
            
            # Build playlists
            playlist1 = indexer.build_playlist(index, start_index1, playlist_size)
            playlist2 = indexer.build_playlist(index, start_index2, playlist_size)
            
            # Calculate similarity
            similarity = calculate_playlist_similarity(indexer, playlist1, playlist2)
            total_similarity += similarity
        
        # Calculate average similarity
        avg_similarity = total_similarity / n_pairs
        logging.info(f"Average similarity score: {avg_similarity}")
        
        # Return similarity for maximization
        return avg_similarity
    
    except Exception as e:
        logging.error(f"Playlist generation or similarity calculation failed: {str(e)}")
        return float('inf')

def main():
    """Main function to run the optimization."""
    # Create study with timestamped database
    study = optuna.create_study(
        study_name=f"playlist_optimization_{timestamp}",
        direction="maximize",
        storage=f"sqlite:///{study_db}",
        load_if_exists=True
    )
    
    # Run optimization
    n_trials = 200
    logging.info(f"Starting optimization with {n_trials} trials")
    
    try:
        study.optimize(objective, n_trials=n_trials)
        
        # Log results
        logging.info("\n=== Optimization Results ===")
        logging.info(f"Number of finished trials: {len(study.trials)}")
        logging.info("\nBest trial:")
        trial = study.best_trial
        
        logging.info(f"  Value: {trial.value}")
        logging.info("  Params:")
        for key, value in trial.params.items():
            logging.info(f"    {key}: {value}")
        
        # Save results to file
        with open(results_file, 'w') as f:
            f.write("=== Optimization Results ===\n")
            f.write(f"Optimization completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Best value: {trial.value}\n")
            f.write("Best parameters:\n")
            for key, value in trial.params.items():
                f.write(f"  {key}: {value}\n")
            
            # Add additional statistics
            f.write("\nOptimization Statistics:\n")
            f.write(f"Total number of trials: {len(study.trials)}\n")
            f.write(f"Number of completed trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])}\n")
            f.write(f"Number of failed trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.FAIL])}\n")
            
            # Add study parameters
            f.write("\nStudy Parameters:\n")
            f.write(f"Study name: {study.study_name}\n")
            f.write(f"Optimization direction: {study.direction.name}\n")
            f.write(f"Study database: {study_db}\n")
            f.write(f"Log file: {log_file}\n")
        
        logging.info(f"Results saved to: {results_file}")
    except Exception as e:
        logging.error(f"Optimization failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
