import logging
import requests
import re
from bs4 import BeautifulSoup
import os
from keys import genius_access_token
import spacy
from collections import defaultdict
from constants import SUBJECTS

# Load spaCy model at module level (only happens once)
try:
    nlp = spacy.load('en_core_web_md')  # Medium-sized model with word vectors
except OSError:
    # If model isn't installed, provide instructions
    raise OSError("Please install the spaCy model by running: python -m spacy download en_core_web_md")

def get_lyrics_genius(song_title, artist_name, subject_list=SUBJECTS):
    """
    Get language, release date, and subject using Genius API and web scraping
    
    Args:
        song_title (str): The song title
        artist_name (str): The artist name
        subject_list (list): List of predefined subjects to match against
        
    Returns:
        tuple: (language, release_date, subject) or (None, None, None) if not found
    """
    base_url = 'https://api.genius.com'
    headers = {'Authorization': f'Bearer {genius_access_token}'}
    search_url = f"{base_url}/search"
    
    params = {
        'q': f"{song_title} {artist_name}"
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        json_data = response.json()
        
        for hit in json_data['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_url = hit['result']['url']
                
                # Get song details to extract language and release date
                song_api_path = hit['result']['api_path']
                song_response = requests.get(f"{base_url}{song_api_path}", headers=headers)
                song_data = song_response.json()
                language = song_data['response']['song'].get('language', 'unknown')
                release_date = song_data['response']['song'].get('release_date', 'unknown')
                
                # Get lyrics from webpage
                page = requests.get(song_url)
                soup = BeautifulSoup(page.content, 'html.parser')
                
                lyrics_containers = soup.select('div[class*="Lyrics__Container"]')
                if lyrics_containers:
                    lyrics = '\n'.join([container.get_text() for container in lyrics_containers])
                    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
                    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s.strip()])
                    
                    # Extract subject using spaCy if subject_list is provided
                    subject = None
                    if subject_list and lyrics:
                        subject = extract_subject_with_spacy(lyrics, subject_list)
                    
                    return language, release_date, subject
                
        return None, None, None
        
    except Exception as e:
        logging.error(f"Error fetching lyrics: {e}")
        return None, None, None

def extract_subject_with_spacy(lyrics, subject_list):
    """
    Extract the most relevant subject from lyrics using spaCy's word vectors
    """
    doc = nlp(lyrics.lower())
    
    # Create spaCy docs for subjects
    subject_docs = [nlp(subject.lower()) for subject in subject_list]
    
    subject_scores = defaultdict(float)
    relevant_pos = {'NOUN', 'VERB', 'ADJ', 'PROPN'}
    
    # Only process words that have vectors
    meaningful_words = [token for token in doc 
                       if token.pos_ in relevant_pos 
                       and not token.is_stop 
                       and token.has_vector]
    
    # Calculate similarity scores
    for word in meaningful_words:
        for subject_doc, subject in zip(subject_docs, subject_list):
            # Only consider subject tokens with vectors
            subject_tokens = [token for token in subject_doc if token.has_vector]
            if subject_tokens:  # Only proceed if we have valid tokens
                similarity = max(word.similarity(subject_token) 
                               for subject_token in subject_tokens)
                subject_scores[subject] += similarity
    
    if not subject_scores:
        return None
    
    # Normalize scores
    for subject in subject_scores:
        subject_scores[subject] /= len(meaningful_words) if meaningful_words else 1
    
    # Lower threshold since we're being more selective with words
    best_subject, best_score = max(subject_scores.items(), key=lambda x: x[1])
    threshold = 0.2  # Adjusted threshold
    
    return best_subject if best_score > threshold else None


if __name__ == "__main__":

    language, release_date, subject = get_lyrics_genius("Yesterday", "The Beatles", SUBJECTS)  
    print(f"Language: {language}")
    print(f"Release Date: {release_date}")
    print(f"Subject: {subject}")
