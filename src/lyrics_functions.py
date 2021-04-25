import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer as PS
from nltk.stem.snowball import SnowballStemmer as SS
from nltk.stem.wordnet import WordNetLemmatizer as WNL

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

import unicodedata
import string
import numpy as np
import pandas as pd
import re

import lyricsgenius
genius = lyricsgenius.Genius('8RrM66Ch9ov3QcGvV5KKkTwHTsnZpb2FRW2Jgvx04Me3sq9Duozolc0aoXpoIsKo', timeout=15,
                                sleep_time=1, retries=5) 

df = pd.read_csv('../my_albums.csv', engine='python')

def clean_lyrics(lyrics_str):
    lyr_clean = re.sub("[\(\[].*?[\)\]]", "", lyrics_str)
    lyr_clean = lyr_clean.rstrip()
    lyr_clean = lyr_clean.splitlines()
    return lyr_clean # Is a list of strings as bars from the lyrics

def get_song_lyrics(song, artist):
    song = genius.search_song(song, artist)
    return song.to_text()

def loop_songs_for_lyrics(df):
    for i in range(len(df.index)):
        song = genius.search_song(df.index[i][1], df.index[i][2])
        
        if song is None:
            print(f"Unable to find {df.index[i][1]} on Genius search...")
            if i == 0:
                ser_lyrics = pd.Series('no lyrics found')
            else:
                ser_lyrics.append(pd.Series('no lyrics found'))
            continue
            
        lyrics = song.to_text()
        cleaned_lyrics = clean_lyrics(lyrics)

        if i == 0:
            ser_lyrics = pd.Series(lyrics)
        else:
            ser_lyrics.append(pd.Series(lyrics))
    
    return ser_lyrics

    # df['song_lyrics'] = ser_lyrics.T.values
    
    # return df
    
def get_album_lyrics(df):
    # Making sure all Titles are read in as strings
    df['Title'] = df['Title'].map(str)

    lyrics_dict = {}

    for i in range(len(df['Title'])):
        song = genius.search_song(df['Title'][i], df['Artist'][i])
        if song is None:
            print(f'Nothing found for {df["Title"][i]}', '\n')
            continue
        lyrics = song.to_text()
        lyrics_dict[df['Title'][i]] = lyrics


    return lyrics_dict


def niave_bayes_album(documents, df_albums):
    count_vect = CountVectorizer(stop_words='english')

    count_vect.fit(documents)

    X_train_counts = count_vect.transform(documents)
    print('\n', "The type of X_train_counts is {0}.".format(type(X_train_counts)))
    print("The X matrix has {0} rows (documents) and {1} columns (words).".format(
            X_train_counts.shape[0], X_train_counts.shape[1]), '\n')
    
    tfidf_transformer = TfidfTransformer()
    tfidf_transformer.fit(X_train_counts)
    X_train_tfidf = tfidf_transformer.transform(X_train_counts)

    tfidf_df = pd.DataFrame(X_train_tfidf.todense(), columns = count_vect.vocabulary_)

    words = np.array(list(count_vect.vocabulary_.keys()))

    #calculating the sum and mean of the tfidfs
    tfidf_totals = np.array(tfidf_df.sum())

    #(tfidf_df>0).sum() gives us the sum of all non-zero values
    tfidf_means = np.array(tfidf_totals/(tfidf_df>0).sum())

    print('\n', f'TFIDF Means: {tfidf_means}', '\n')

    #fancy indexing to get top 10

    top10_totals = np.argsort(tfidf_totals)[-10:][::-1].tolist()
    print(f'Top ten total words {words[top10_totals]}')
    df_albums['top_total_words'] = [top10_totals]

    #fancy indexing to get top 10
    # top10_means = np.argsort(tfidf_means)[-10:][::-1].tolist()
    # print(f'Top ten mean words {words[top10_means]}')
    # df_albums['top_mean_words'] = top10_means

    return df_albums
