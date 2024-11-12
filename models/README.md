# Models Folder

The `models` folder contains the core components of the application, responsible for data processing, indexing, and similarity computations related to songs and playlists.

## Files

### `indexing.py`

- **Purpose:**  
  Defines the `SongIndexer` class, which handles loading and preprocessing song data, creating FAISS indexes for efficient similarity searches, and building playlists based on song similarities.

- **Key Features:**
  - **Data Loading and Preprocessing:**  
    Loads song data from CSV files, normalizes selected features, and reduces dimensionality using PCA.
  
  - **Index Creation:**  
    Creates various types of FAISS indexes (`FlatL2`, `FlatIP`, `HNSWFlat`, `IVFFlat`, `IVFPQ`) based on specified parameters to optimize similarity search performance.
  
  - **Playlist Building:**  
    Generates playlists by iteratively searching for the most similar songs using the created FAISS index.
  
  - **Utility Functions:**  
    Retrieves song names based on playlist indices for easy interpretation of generated playlists.

- **Usage Example:**
  ```bash
  python models/indexing.py
  ```
  This will execute the `test_indices` function, which demonstrates how to create different FAISS indexes and generate playlists based on song features.

## Usage

To use the components in the `models` folder:

1. **Ensure Data Availability:**  
   Place the required CSV files (e.g., `rock_songs_features.csv`) in the `data` directory.

2. **Run the Script:**  
   Execute the desired script using Python. For example:
   ```bash
   python models/indexing.py
   ```
