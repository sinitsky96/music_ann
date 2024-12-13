# Music ANN Playlist Generator

A machine learning system that generates personalized music playlists using artificial neural networks to analyze audio features, lyrics, and musical characteristics. This university project uses the Spotify API and advanced similarity metrics with FAISS indexing to create cohesive playlists that maintain consistent mood and style.

## Overview

The system follows a pipeline approach:
1. Collects millions of songs via Spotify API
2. Preprocesses the data to create feature vectors for each song
3. Chooses playlists as ground truth for training
4. Uses weighted vectors and FAISS indexing for similarity search
5. Creates playlists using ANN-based similarity matching
6. Evaluates generated playlists against base playlists
## Overview

The system follows a pipeline approach:
1. Collects millions of songs via Spotify API
2. Preprocesses the data to create feature vectors for each song
3. Chooses playlists as ground truth for training
4. Uses weighted vectors and FAISS indexing for similarity search
5. Creates playlists based on input songs
6. Evaluates generated playlists against base playlists

**API Configuration**
Create a `keys.py` file with:
- `client_id = "your_spotify_client_id"`
- `client_secret = "your_spotify_client_secret"`
- `genius_access_token = "your_genius_access_token"`


## Key Features

### Data Collection & Processing
- Fetches song data and audio features from Spotify API
- Collects and analyzes lyrics using Genius API
- Normalizes features and reduces dimensionality
- Creates efficient similarity indices using FAISS

### Neural Network Architecture
- Implements ANN for song similarity learning
- Trains on existing playlist patterns
- Optimizes feature weights for better matching
- Adapts to different musical styles and preferences

### Indexing & Search
- Uses FAISS (Facebook AI Similarity Search) for efficient similarity search
- Implements IVF (Inverted File Index) for fast approximate nearest neighbor search
- Reduces high-dimensional song features to optimized search vectors
- Enables quick retrieval of similar songs from millions of entries

### Hyperparameter Optimization
- Uses Optuna for automated hyperparameter tuning
- Optimizes FAISS index configurations for better similarity search
- Tunes parameters like:
  - Number of components for dimensionality reduction
  - Index types (FlatL2, FlatIP, HNSWFlat, IVFFlat, IVFPQ)
  - Number of clusters and probe points
  - Product quantization parameters
- Logs optimization results and performance metrics

### Playlist Generation
- ANN-based similarity matching
- Mood and style consistency maintenance through feature weighting
- Configurable playlist length and characteristics
- Iterative song selection based on learned patterns

### Evaluation Metrics
- Centroid distance between playlists
- Cosine similarity measurements
- Average pairwise distance calculations
- Playlist coherence evaluation
