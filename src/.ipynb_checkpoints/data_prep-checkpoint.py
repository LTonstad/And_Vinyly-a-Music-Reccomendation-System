import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
from PIL import Image
import requests
import matplotlib.pyplot as plt

df_main = pd.read_csv('data/my_albums.csv')

def get_album_avgs(df_main):
    album_avgs = df_main.groupby('album')['year', 'featured_artists', 'tracks_on_album',
                        'explicit', 'duration_ms', 'popularity','danceability', 'energy', 
                        'key', 'loudness', 'mode', 'speechiness', 'acousticness', 
                        'instrumentalness', 'liveness', 'valence', 'tempo',
                        'tempo_confidence', 'track_length', 'end_fade_in', 'start_fade_out',
                        'end_silence_time'].agg(np.mean)

    # Changing values to integers
    album_avgs['year'] = album_avgs['year'].astype('int')
    album_avgs['tracks_on_album'] = album_avgs['tracks_on_album'].astype('int')
    album_avgs['explicit'] = album_avgs['explicit'].astype('int')

    ratings = albums['Rating'].to_numpy(dtype='int')
    album_avgs['ratings'] = ratings

    return album_avgs