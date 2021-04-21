import numpy as np
import pandas as pd

df_main = pd.read_csv('data/my_albums.csv')

def split_df_columns(df):
    # Multi-indexing with album and name of song
    new_df = df.set_index(['album','name'], inplace=True)
    
    # Creating bool value for if an there is an artist feature in the song
    new_df['has_featured_artist'] = np.where(new_df['featured_artists'].isna(), 0, 1)
    
    # Filling featured artists with 'No Features' as a string
    new_df['featured_artists'].fillna('No Features', inplace=True)
    
    # To get all columns with string values
    df_str = new_df[['artist', 'featured_artists', 'release_date', 'album_label', 'artist_genres']]
    
    # For columns with referential values, like link to artist profile, album image link etc.
    df_ref = new_df[['id', 'uri', 'track_href', 'analysis_url', 'artist_uri', 'album_uri',
                 'album_image_url', 'artist_spotify_link']]
    
    # For all numerical columns
    df_num = new_df[['year', 'has_featured_artist', 'track_number', 'tracks_on_album', 'explicit', 'duration_ms', 'popularity',
              'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
              'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'followers', 'artist_popularity',
              'track_length', 'tempo_confidence', 'end_fade_in', 'start_fade_out','end_silence_time']]
    
    # For advanced, analytics columns
    df_arrs = new_df[['sections', 'tatums', 'beats', 'bars']]
    
    return df_str, df_ref, df_num, df_arrs

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