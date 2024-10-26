# Audio Features Explanation

This document explains the audio features extracted from the Spotify Web API. Each feature provides unique insights into the musical and acoustic properties of tracks.

## Acoustic Characteristics

### Acousticness (0.0 to 1.0)
- Measures confidence that the track is acoustic
- Higher values (closer to 1.0) indicate higher confidence of being acoustic
- Example: A value of 0.95 suggests the track is likely acoustic

### Instrumentalness (0.0 to 1.0)
- Predicts whether a track lacks vocals
- Values above 0.5 likely indicate instrumental tracks
- "Ooh" and "aah" sounds are considered instrumental
- Rap and spoken word are classified as vocal
- Higher confidence as value approaches 1.0

## Musical Qualities

### Danceability (0.0 to 1.0)
- Evaluates how suitable a track is for dancing
- Based on tempo, rhythm stability, beat strength, and regularity
- 0.0 = least danceable, 1.0 = most danceable

### Energy (0.0 to 1.0)
- Represents intensity and activity
- Considers dynamic range, loudness, timbre, onset rate, and entropy
- High energy: Death metal (loud, fast, noisy)
- Low energy: Bach prelude (calm, subtle)

### Valence (0.0 to 1.0)
- Measures musical positiveness
- High valence (closer to 1.0): happy, cheerful, euphoric
- Low valence (closer to 0.0): sad, depressed, angry

## Technical Attributes

### Key (-1 to 11)
- Represents the musical key using Pitch Class notation
- 0 = C, 1 = C♯/D♭, 2 = D, etc.
- -1 indicates no detected key

### Loudness (typically -60 to 0 dB)
- Overall track loudness in decibels
- Averaged across entire track
- Used for comparing relative loudness between tracks

### Mode (0 or 1)
- Indicates track modality
- 0 = minor key
- 1 = major key

### Tempo (BPM)
- Estimated beats per minute
- Represents the speed/pace of the track

### Time Signature (3 to 7)
- Indicates beats per measure
- Range represents time signatures from 3/4 to 7/4

## Performance Indicators

### Liveness (0.0 to 1.0)
- Detects audience presence
- Values above 0.8 strongly suggest a live recording
- Higher values indicate higher probability of live performance

### Speechiness (0.0 to 1.0)
- Detects spoken words presence
- Above 0.66: Likely entirely spoken (talk shows, audiobooks)
- 0.33-0.66: May contain both music and speech (e.g., rap)
- Below 0.33: Likely music with no speech

## Duration

### Duration_ms
- Track length in milliseconds
- Raw numerical value


### Lyrics
- Lyrics of the track (from Genius API)

---
*Source: [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)*

