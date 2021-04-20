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

# Making sure all Titles are read in as strings
albums['Title'] = albums['Title'].map(str)

# Ratings array
ratings = albums['Rating'].to_numpy(dtype='int')

def get_song_data(track, year, artist):
      
    """
    This function returns a dataframe with data for a song given the name and release year.
    The function uses Spotipy to fetch audio features and metadata for the specified song.
    
    """
    
    song_data = defaultdict()
    results = sp.search(q='track: {} year: {} artist: {}'.format(track, year, artist), type="track", limit=1)
    if results['tracks']['items'] == []:
        return None
    
    results = results['tracks']['items'][0]

    track_id = results['id']
    
    # Audio_Features section
    audio_features = sp.audio_features(track_id)[0]
    
    song_data['name'] = [track]
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
    
    song_data['artist_uri'] = [results['album']['artists'][0]['uri']]
    song_data['album_uri'] = [results['album']['uri']]
    song_data['release_date'] = [results['album']['release_date']]
    song_data['album_image_url'] = [results['album']['images'][0]['url']]

    # Audio Analysis Section
    aa = sp.audio_analysis(track_id)

    song_data['track_length'] = [aa['track']['duration']]
    song_data['tempo_confidence'] = [aa['track']['tempo_confidence']]
    song_data['end_fade_in'] = [aa['track']['end_of_fade_in']]
    song_data['start_fade_out'] = [aa['track']['start_of_fade_out']]
    song_data['end_silence_time'] = aa['track']['duration'] - aa['track']['start_of_fade_out']

    # Adding dict columns from audio analysis
    song_data['sections'] = [aa['sections']]
    song_data['tatums'] = [aa['tatums']]
    song_data['beats'] = [aa['beats']]
    song_data['bars'] = [aa['bars']]
    
    return pd.DataFrame(song_data)


# Get dictionary for inputs into the get_song_data function
def get_songs_on_album(album_idx):
    album = albums['Title'][album_idx]
    year = albums['Released'][album_idx]
    artist = albums['Artist'][album_idx]

    # find album by name
    results = sp.search('album: {} year: {} artist: {}'.format(album, year, artist), type = "album")

    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp.album_tracks(album_id)

    print('\n' + f'Getting songs for {album}' + '\n')
    
    for idx, track in enumerate(tracks['items']):
        if idx == 0:
            album_df = get_song_data(track['name'], year, artist)
        else:
            song_df = get_song_data(track['name'], year, artist)
            album_df = album_df.append(song_df, ignore_index=True)

        print(track['name'])

    print('\n' + f'Done getting songs for {album}' + '\n')

    return album_df

def get_album_df(file_name='my_albums'):
    for album_idx in range(len(albums['Title'])):
        if album_idx == 0:
            df = get_songs_on_album(album_idx)
            img = Image.open(requests.get(df['album_image_url'][0], stream=True).raw)
        else:
            album_df = get_songs_on_album(album_idx)
            df = df.append(album_df)
            img = Image.open(requests.get(album_df['album_image_url'][0], stream=True).raw)
        plt.imshow(img)
        plt.show()

    df.to_csv('../data/{file_name}.csv')

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