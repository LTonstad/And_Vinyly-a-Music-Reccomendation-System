import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
from PIL import Image
import requests
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

# Taken from here: https://towardsdatascience.com/how-to-build-an-amazing-music-recommendation-system-4cce2719a572
# Returns 1 column dataframe with all the song features

# How to print album art:
# Image.open(requests.get(df_song['album_image_url'][0], stream=True).raw)

# Setup Authentication
auth_manager = SpotifyClientCredentials('424af1dc12124b348f3512f327311c06', '4f653f97baa9452984c3a2dc2d202024')
sp = spotipy.Spotify(auth_manager=auth_manager)

# Pull in my Album Data
albums = pd.read_excel('data/my_albums.ods')

def get_song_data(name, year):
      
    """
    This function returns a dataframe with data for a song given the name and release year.
    The function uses Spotipy to fetch audio features and metadata for the specified song.
    
    """
    
    song_data = defaultdict()
    results = sp.search(q= 'track: {} year: {}'.format(name, year), limit=1)
    if results['tracks']['items'] == []:
        return None
    
    results = results['tracks']['items'][0]

    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]
    
    song_data['name'] = [name]
    song_data['album'] = [results['album']['name']]
    song_data['year'] = [year]

    if len(results['artists']) > 1:
        for idx, i in enumerate(results['artists']):
            if idx == 0:
                song_data['artist'] = results['artists'][idx]['name']
            else:
                song_data['featured_artists'] = results['artists'][idx]['name']
    else:
        song_data['artist'] = results['artists'][0]['name']

    song_data['track_number'] = [results['track_number']]
    song_data['tracks_on_album'] = [results['album']['total_tracks']]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

    for key, value in audio_features.items():
        song_data[key] = value
    
    song_data['album_image_url'] = [results['album']['images'][0]['url']]

    return pd.DataFrame(song_data)


def get_song_dict(album_idx):
    d = defaultdict(list)
    album = albums['Title'][album_idx]
    year = albums['Released'][album_idx]

    # find album by name
    results = sp.search(q = "album:" + album, type = "album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp.album_tracks(album_id)

    print(f'Getting songs for {album}' + '\n')
    for track in tracks['items']:
        d['name'].append(track['name'])
        d['year'].append(year)
        print(track['name'])

    print(f'Done getting songs for {album}' + '\n')

    return d