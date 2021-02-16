import requests
import urllib.request
import urllib.parse
import json
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import lyricsgenius
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from datetime import datetime

#nltk.download('stopwords')
#nltk.download('wordnet')

######################################################################
########### Main file to run everything #############################
#####################################################################

# Constants
base = "https://api.genius.com"

path_cred = "../../"
f = open(path_cred + "genius_credentials.txt", "r")
dict_credentials = json.loads(f.read()[:-1])

genius = lyricsgenius.Genius(dict_credentials["client_id"])

genius.verbose = True # Turn off status messages
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.skip_non_songs = False # Include hits thought to be non-songs (e.g. track lists)
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title

def clean_lyrics(lyrics):
    """
    This function cleans the words without importance and fix the format of the  dataframe's column lyrics
    parameters:
    lyrics: original string coming from Genius
    """
    lyrics = lyrics.lower()
    lyrics = lyrics.replace(r"verse |[1|2|3]|chorus|bridge|outro","").replace("[","").replace("]","")
    lyrics = lyrics.lower().replace(r"instrumental|intro|guitar|solo","")
    lyrics = lyrics.replace("\n"," ").replace(r"[^\w\d'\s]+","").replace("efil ym fo flah","")
    lyrics = lyrics.strip()
    return lyrics

def lyrics_to_words(lyrics):
    """
    This function splits the text of lyrics to  single words, removing stopwords and doing the lemmatization to each word
    parameters:
    lyrics: text to split to single words
    """
    stop_words = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()
    stopwordremoval = " ".join([i for i in lyrics.lower().split() if i not in stop_words])
    punctuationremoval = ''.join(ch for ch in stopwordremoval if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punctuationremoval.split())
    return normalized

def main():
    """
    This is the main function:
    1) reads all songs from the DataFrame coming from Spotify
    2) get lyrics from genius
    3) clean lyrics
    4) add the list of the unique words in each song
    """
    songs_df = pd.read_csv("../data/songs_all.csv")
    words_lyrics = []

    start = datetime.now()

    for i in range(len(songs_df)):
        print("Song: " + str(i+1) + "/" + str(len(songs_df)))
        song_name = songs_df.name[i]
        artist_name = songs_df.artist_1[i]
        if "-" in song_name:
            song_name = song_name.split(" - ")[0]
        song = genius.search_song(song_name, artist_name)
        if song == None:
            words_lyrics.append(None)
        else:
            lyrics_song = song.lyrics
            if len(lyrics_song) == 0:
                words_lyrics.append(None)
            else:
                cleaned_lyrics = clean_lyrics(lyrics_song)
                words_lyrics.append(list(set(lyrics_to_words(cleaned_lyrics).split())))

    stop = datetime.now()

    print("Time spend:", stop-start, "- Average by song:", (stop-start)/len(songs_df))

    songs_df['words_lyrics'] = words_lyrics

    songs_df.to_csv("../data/songs_lyrics.csv", index=False)

if __name__ == "__main__":
    main()
