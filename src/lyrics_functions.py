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

import lyricsgenius
genius = lyricsgenius.Genius('8RrM66Ch9ov3QcGvV5KKkTwHTsnZpb2FRW2Jgvx04Me3sq9Duozolc0aoXpoIsKo')

def get_album_lyrics(album, artist):
    lyrics_dict = {}

    for i in range(len(df_nsp['name'])):
        song = genius.search_song(df_nsp['name'][i], df_nsp['artist'][i])
        lyrics = song.to_text()
        lyrics_dict[df_nsp['name'][i]] = lyrics

    documents = lyrics_dict.values()

    return documents, lyrics_dict


def niave_bayes_album(documents, df_albums):
    count_vect = CountVectorizer(stop_words='english')

    count_vect.fit(documents)

    X_train_counts = count_vect.transform(documents)
    print("The type of X_train_counts is {0}.".format(type(X_train_counts)))
    print("The X matrix has {0} rows (documents) and {1} columns (words).".format(
            X_train_counts.shape[0], X_train_counts.shape[1]))
    
    tfidf_transformer = TfidfTransformer()
    tfidf_transformer.fit(X_train_counts)
    X_train_tfidf = tfidf_transformer.transform(X_train_counts)

    tfidf_df = pd.DataFrame(X_train_tfidf.todense(), columns = count_vect.vocabulary_)

    words = np.array(list(count_vect.vocabulary_.keys()))

    #calculating the sum and mean of the tfidfs
    tfidf_totals = np.array(tfidf_df.sum())

    #(tfidf_df>0).sum() gives us the sum of all non-zero values
    tfidf_means = np.array(tfidf_totals/(tfidf_df>0).sum())

    #fancy indexing to get top 10
    top10_totals = np.argsort(tfidf_totals)[-10:][::-1].tolist()
    print(f'Top ten total words {words[top10_totals]}')
    df_albums['top_total_words'] = top10_totals

    #fancy indexing to get top 10
    top10_means = np.argsort(tfidf_means)[-10:][::-1].tolist()
    print(f'Top ten mean words {words[top10_means]}')
    df_albums['top_mean_words'] = top10_means

    return df_albums