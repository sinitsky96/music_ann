# eval

The `eval` folder contains scripts designed to evaluate and optimize song similarity metrics and playlist generation using various machine learning techniques. Below is an overview of each file within the folder.

## Files

### `optuna_hyperparameter_tuning.py`

This script leverages Optuna to perform hyperparameter optimization for the `SongIndexer` model. The goal is to enhance the performance of playlist similarity metrics by fine-tuning various model parameters. It logs the optimization process and saves the results for further analysis.

### `similarity_playlist.py`

This script is responsible for generating playlists based on song features and computing similarity metrics between them. It utilizes FAISS for efficient nearest neighbor searches and applies PCA for dimensionality reduction to improve performance. The script calculates metrics such as centroid distance, cosine similarity, and average pairwise distance between playlists.

### `similarity_song.py`

This script calculates similarity metrics between individual songs using normalized features. It provides both cosine similarity and Euclidean distance measures to assess how similar two songs are based on their attributes. The script ensures data integrity by removing duplicate songs and normalizing feature data for consistent similarity calculations.

## Usage

To run any of the scripts, navigate to the `eval` folder and execute the desired Python script. Ensure that all necessary data files are placed in the appropriate `data` directory and that all dependencies are installed.
