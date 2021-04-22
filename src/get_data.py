import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
from PIL import Image
import requests
import matplotlib.pyplot as plt

# Setup Authentication
auth_manager = SpotifyClientCredentials('424af1dc12124b348f3512f327311c06',  '4f653f97baa9452984c3a2dc2d202024')
sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=5, 
                    retries=15, status_retries=10, backoff_factor=1)

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
    results = sp.search(q='track: {} year: {} artist: {}'.format(str(track), int(year), str(artist)), type="track", limit=1)
    
    # Checking if error in search results
    if results['tracks']['items'] == []:
        return None
    elif results is None:
        return None
    
    # Making life easier for the rest of dictionary slicing
    results = results['tracks']['items'][0]
    track_id = results['id']
    
    # Audio_Features section
    audio_features = sp.audio_features(track_id)[0]
    
    song_data['name'] = [track]
    song_data['album'] = [results['album']['name']]
    song_data['year'] = [year]
    
    # Getting artist names within loop, dependent on if there is multiple artists
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
    
    # Getting some other columns based on album search
    # First to change what I use in place of 'results'
    album_results = sp.album(results['album']['uri'])
    
    # Now to get other data from album that we couldn't from song
    song_data['album_label'] = [album_results['label']]
    
    # Same with artist data
    artist_results = sp.artist(results['album']['artists'][0]['uri'])
    
    song_data['artist_spotify_link'] = [artist_results['external_urls']['spotify']]
    song_data['followers'] = [artist_results['followers']['total']]
    song_data['artist_genres'] = [artist_results['genres']]
    song_data['artist_image_url'] = [artist_results['images'][0]['url']]
    song_data['artist_popularity'] = [artist_results['popularity']]
    
    # Adding dict columns from audio analysis, these columns are extremely large
    song_data['sections'] = [aa['sections']]
    song_data['tatums'] = [aa['tatums']]
    song_data['beats'] = [aa['beats']]
    song_data['bars'] = [aa['bars']]
    
    return pd.DataFrame(song_data)


# Get dictionary for inputs into the get_song_data function
def get_songs_on_album(album_idx, df_albums):
    album = df_albums['Title'][album_idx]
    year = df_albums['Released'][album_idx]
    artist = df_albums['Artist'][album_idx]

    # find album by name
    results = sp.search('album: {} year: {} artist: {}'.format(str(album), int(year), str(artist)), type = "album")
    
    if results['albums']['items'] == []:
        return None
    elif results is None:
        return None
    
    # get the first album uri
    album_id = results['albums']['items'][0]['uri']

    # get album tracks
    tracks = sp.album_tracks(album_id)

    print('\n' + f'Getting songs for {album}' + '\n')
    
    # Looping through track names to load into get_song_data function
    for idx, track in enumerate(tracks['items']):
        # To create df if it's not already created
        if idx == 0:
            album_df = get_song_data(track['name'], year, artist)
            # Error checking...
            if album_df is None:
                print('Unable to find song :(')
                continue
        else:
            song_df = get_song_data(track['name'], year, artist)
            # Error checking...
            if song_df is None or album_df is None:
                print('Unable to find song :(')
                continue
            else:
                album_df = album_df.append(song_df, ignore_index=True)

        print(track['name'])

    print('\n' + f'Done getting songs for {album}' + '\n')

    return album_df

# This function essentially puts it all together, just need to make sure the column names match
def get_album_df(df_album, file_name):
    # Iterates through the amount of times that is equal to the amount of album titles in the dataframe
    for album_idx in range(len(df_album['Title'])):
        # To create Dataframe on first round through
        if album_idx == 0:
            df = get_songs_on_album(album_idx, df_album)
            # Checks to verify that Spotipy api was able to find the album or not, prints the error
            # and moves to the next album if that is the case
            if df is None:
                print('Album was not found...')
                continue
            # Captures image to be printed by MatPlotLib at the end of the loop
            img = Image.open(requests.get(df['album_image_url'][0], stream=True).raw)
        else:
            album_df = get_songs_on_album(album_idx, df_album)
            if album_df is None:
                print('Album was not found...')
                continue
            df = df.append(album_df)
            img = Image.open(requests.get(album_df['album_image_url'][0], stream=True).raw)
        # Prints album artwork once it's completed with this album
        plt.imshow(img)
        plt.show()

    # Saves resulting DataFrame with the given name to the data folder as a .csv file
    df.to_csv(f'data/{file_name}.csv')
    
    return album_df