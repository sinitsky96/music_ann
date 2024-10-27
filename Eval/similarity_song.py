import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def normalize_features_df(df, descriptive_columns):
    """
    Normalize the feature columns of a dataframe.

    Args:
        df (pandas.DataFrame): The dataframe containing both descriptive and feature columns.
        descriptive_columns (List[str]): List of column names that should not be normalized.

    Returns:
        pandas.DataFrame: A dataframe with normalized feature columns.
    """
    feature_columns = [col for col in df.columns.tolist()
                       if col not in descriptive_columns]
    df_features = df[feature_columns]
    df_normalized = (df_features - df_features.mean()) / df_features.std()

    # If the entire column is zero, normalize to zero instead of NaN
    df_normalized = df_normalized.fillna(0)
    return df_normalized


def calculate_similarity(song1, song2):
    cosine_sim = cosine_similarity(song1, song2)
    euclidean_dist = np.linalg.norm(song1 - song2)

    return cosine_sim[0][0], euclidean_dist


# test the functions
if __name__ == "__main__":
    df = pd.read_csv("data/playlist_songs_features.csv")

    # remove duplicate rows
    df = df.drop_duplicates(subset=["track_id"])

    descriptive_columns = ["playlist_name", "track_id", "track_name",
                           "artist", "genre", "lyrics", "release_date", "language"]
    df_normalized = normalize_features_df(df, descriptive_columns)

    song1 = df_normalized.iloc[0].values.reshape(1, -1)
    song2 = df_normalized.iloc[1].values.reshape(1, -1)

    cosine_sim, euclidean_dist = calculate_similarity(song1, song2)

    print("Cosine Similarity:", cosine_sim)
    print("Euclidean Distance:", euclidean_dist)
