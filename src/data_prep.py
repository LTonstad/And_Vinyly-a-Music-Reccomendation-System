import numpy as np
import pandas as pd

df_genre = pd.read_csv('data/genre_matrix.csv', index_col=0)

# Creates the df_genre csv above
# Useful when more music comes in to get any new genres
def get_genres_series_alt(df):
    # This is an alterate to the original get_genres_series
    # Used for cases that the 'artist_genres' are already lists
    genre_dict = {}

    for i in range(len(df['artist_genres'])):
        
        stringA = df['artist_genres'].iloc[i]
        
        for genre in stringA:
            if genre in genre_dict:
                genre_dict[genre] += 1
            else:
                genre_dict[genre] = 1

    return pd.Series(genre_dict)

# Will need to be made after df_genre to get columns properly
# This is used for 2010s data, genres were passed as list instead of string
def add_genre_vals_alt(df, df_genre):
    # Gets all Genres in a list of strings
    genre_cols = df_genre.columns

    # Needed if there is an empty string for Genre
    if '' in df.columns:
        df['unknown'] = df['']
        del df['']

    # Adds the columns with nans as placeholders
    for col in genre_cols:
        print(f'Adding {col}')
        df[col] = np.nan
    
    # Loops through and adds 1 to rows that the song is considered a part of that genre
    # leaves values as nans otherwise
    for i in range(len(df['artist_genres']) - 1):

        stringA = df['artist_genres'].iloc[i]

        for genre in stringA:
            if genre in df.columns:
                df.loc[:, (genre, i)] = 1
                print(i)
    
    df.fillna(0, axis=1, inplace=True)


