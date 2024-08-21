import os
import pandas as pd
import numpy as np
import librosa
from pydub import AudioSegment
import warnings
from constants import raw_data_path
warnings.filterwarnings("ignore")

def extract_features(wav_file_path):
    try:
        # Load the audio file using pydub
        audio = AudioSegment.from_wav(wav_file_path)
        y = np.array(audio.get_array_of_samples()).astype(np.float32)
        y /= np.iinfo(audio.array_type).max  # Normalize to [-1.0, 1.0]
        sr = audio.frame_rate

        # Convert to mono if stereo
        if audio.channels == 2:
            y = y.reshape((-1, 2)).mean(axis=1)

        # Extract and flatten features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean(axis=1)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr).mean(axis=1)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr).mean(axis=1)
        spectral_flatness = librosa.feature.spectral_flatness(y=y).mean(axis=1)
        
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y).mean(axis=1)
        
        # Ensure all features are 1D and have the correct shape
        features = [
            ('mfcc', mfccs),
            ('chroma', chroma),
            ('spectral_centroid', spectral_centroid),
            ('spectral_bandwidth', spectral_bandwidth),
            ('spectral_contrast', spectral_contrast),
            ('spectral_flatness', spectral_flatness),
            ('tempo', np.array([tempo])),
            ('zero_crossing_rate', zero_crossing_rate)
        ]
        
        # Check dimensions and flatten if necessary
        for i, (name, feat) in enumerate(features):
            if feat.ndim != 1:
                print(f"Feature {name} has {feat.ndim} dimensions. Flattening...")
                features[i] = (name, feat.flatten())
        
        # Combine features into a single vector and create column names
        feature_vector = np.concatenate([feat for _, feat in features])
        column_names = [f"{name}_{i}" for name, feat in features for i in range(len(feat))]
        
        return feature_vector, column_names
    except Exception as e:
        print(f"Error processing {wav_file_path}: {str(e)}")
        return None, None

def convert_wav_to_csv(wav_file_path, csv_file_path, genre):
    # Extract features from the WAV file
    features, column_names = extract_features(wav_file_path)
    
    if features is None or column_names is None:
        return None
    
    # Create a DataFrame with the features
    df = pd.DataFrame([features], columns=column_names)
    
    # Add genre column
    df['genre'] = genre
    
    # Save the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)
    
    return df

def convert_all_wav_to_csv(root_dir):
    all_data = []
    for subdir, _, files in os.walk(root_dir):
        genre = os.path.basename(subdir)
        for file in files:
            if file.endswith('.wav'):
                wav_file_path = os.path.join(subdir, file)
                csv_file_path = os.path.splitext(wav_file_path)[0] + '.csv'
                df = convert_wav_to_csv(wav_file_path, csv_file_path, genre)
                if df is not None:
                    all_data.append(df)
                    print(f"Converted {wav_file_path} to {csv_file_path}")
                else:
                    print(f"Failed to convert {wav_file_path}")
    
    return all_data

def combine_csv_files(root_dir):
    all_data = []
    for subdir, _, files in os.walk(root_dir):
        genre = os.path.basename(subdir)
        for file in files:
            if file.endswith('.csv'):
                csv_file_path = os.path.join(subdir, file)
                df = pd.read_csv(csv_file_path)
                if 'genre' not in df.columns:
                    df['genre'] = genre
                all_data.append(df)
                print(f"Added {csv_file_path} to combined data")
    
    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save the combined DataFrame to a single CSV file
    combined_csv_path = os.path.join(root_dir, 'combined_features.csv')
    combined_df.to_csv(combined_csv_path, index=False)
    print(f"Combined all features into {combined_csv_path}")

if __name__ == "__main__":
    root_directory = raw_data_path
    skip_conversion = False  # Set this to True to skip WAV to CSV conversion

    if not skip_conversion:
        convert_all_wav_to_csv(root_directory)
    
    combine_csv_files(root_directory)