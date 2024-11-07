# AI Music Playlist Generator

A machine learning system that generates personalized music playlists by analyzing audio features, lyrics, and musical characteristics. This university project uses the Spotify API and advanced similarity metrics to create cohesive playlists that maintain consistent mood and style.

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
client_id = "your_spotify_client_id"
client_secret = "your_spotify_client_secret"
genius_access_token = "your_genius_access_token"


## Key Features

### Data Collection & Processing
- Fetches song data and audio features from Spotify API
- Collects and analyzes lyrics using Genius API
- Normalizes features and reduces dimensionality
- Creates efficient similarity indices using FAISS

### Playlist Generation
- Similarity-based song selection
- Mood and style consistency maintenance
- Configurable playlist length and characteristics

### Evaluation Metrics
- Centroid distance between playlists
- Cosine similarity measurements
- Average pairwise distance calculations
