###################################

# Functions below wouldn't be used on new data coming in

# Will need to be made after df_genre to get columns properly
def add_genre_vals(df, df_genre):
    # Gets all Genres in a list of strings
    genre_cols = df_genre.columns

    # Needed if there is an empty string for Genre
    if '' in df.columns:
        df['unknown'] = df['']
        del df['']

    # Adds the columns with nans as placeholders
    for col in genre_cols:
        df[col] = np.nan

    # Loops through and adds 1 to rows that the song is considered a part of that genre
    # leaves values as nans otherwise
    for i in range(len(df['artist_genres'])):
        stringA = df['artist_genres'][i].strip('][').split(', ')
        stringA = [x.replace("'", "") for x in stringA]
        for genre in stringA:
            if genre in df.columns:
                df[genre][i] = 1


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

# Takes list of DataFrame Variables, makes Series objects with
# Genres listed as features, then concatenates the genre DataFrames
def get_genre_df(df_lst):
    for df in df_lst:
        df.sort_index(inplace=True)

    result = pd.concat(df_lst, axis=1)
    result.sort_index(inplace=True)
    result.fillna(0, inplace=True)
    result = result.T
    result = result.append(result.sum(numeric_only=True), ignore_index=True)

    gen_dict = {}
    gen_lst = ['2010s', 'Rolling_Stones', 'Mine', 'Totals']
    for idx in range(len(gen_lst)):
        gen_dict[idx] = gen_lst[idx]
    
    result.rename(gen_dict, inplace=True)
    
    return result.astype('int64')

# Returns Pandas series of a dictionary created indicating all the known Genres as keys 
# and then a count for each song that belongs to this particular genre
def get_genres_series(df):
    genre_dict = {}

    for i in range(len(df['artist_genres'])):
        stringA = df['artist_genres'][i].strip('][').split(', ')
        stringA = [x.replace("'", "") for x in stringA]
        for genre in stringA:
            if genre in genre_dict:
                genre_dict[genre] += 1
            else:
                genre_dict[genre] = 1

    return pd.Series(genre_dict)

# For df's that don't have the genre columns yet
def add_pms(df):
    feat_lst = ['tatums', 'beats', 'bars']
    df['duration_seconds'] = df['duration_ms'] / 1000
    df.drop('duration_ms', inplace=True, axis=1)

    for i in range(len(df['duration_seconds'])):
        song_length = df['duration_seconds'][i]
        for feat in feat_lst:
            df[f'{feat}_per_minute'][i] = len(df[feat][i]) / song_length
    
    return df