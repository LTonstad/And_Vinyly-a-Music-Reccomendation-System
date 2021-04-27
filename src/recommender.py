from sklearn.metrics.pairwise import cosine_distances, cosine_similarity, euclidean_distances, pairwise_distances
from sklearn.preprocessing import StandardScaler
from src.get_data import *
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import operator
from collections import Counter
import random
import math
plt.rcParams["axes.grid"] = False

['acousticness', 'artist_popularity', 'bars_per_minute',
       'beats_per_minute', 'danceability', 'end_fade_in',
       'end_silence_time', 'energy', 'explicit', 'followers',
       'has_featured_artist', 'instrumentalness', 'key', 'liveness',
       'loudness', 'mode', 'popularity', 'speechiness', 'start_fade_out',
       'tatums_per_minute', 'tempo', 'tempo_confidence', 'track_number',
       'tracks_on_album', 'valence', 'year', 'duration_minutes']

df_mine = pd.read_pickle('../final_num_mine.pkl')
grouped_mine = pd.read_pickle('../grouped_mine.pkl')
# df_2010s = pd.read_pickle('../num_2010s.pkl') messed up pickle file
df_rolling = pd.read_pickle('../final_num_rolling.pkl')
df_mega_main = pd.read_pickle('../final_num_full.pkl')
grouped_all = pd.read_pickle('../final_grouped_all_albums.pkl')

class ItemRecommender():
    '''
    Content based item recommender
    '''
    def __init__(self, similarity_measure=cosine_similarity):
        self.similarity_matrix = None
        self.item_names = None
        self.similarity_measure = similarity_measure

    
    def fit(self, X):
        '''
        Takes a numpy array of the item attributes and creates the similarity matrix

        INPUT -
            X: NUMPY ARRAY - Rows are items, columns are feature values / or DF
            titles: LIST - List of the item names/titles in order of the numpy arrray
        
        OUTPUT - None


        Notes:  You might want to keep titles and X as attributes to refer to them later

        Create a similarity matrix of item to item similarity
        '''

        lst_of_albums = X.index.get_level_values(1)

        scaler = StandardScaler()
        scale_matrix = scaler.fit_transform(X)

        indices = pd.Series(lst_of_albums)

        count_df = pd.DataFrame(scale_matrix, index=indices.values)

        self.item_counts = X
        self.item_names = X.index
        self.similarity_df = pd.DataFrame(self.similarity_measure(count_df.values, count_df.values),
                index = self.item_names)

        
    def get_recommendations(self, song_name, artist_name, n=20):
        '''
        Returns the top n items related to the item passed in
        INPUT:
            item    - STRING - Name of item in the original DataFrame 
            n       - INT    - Number of top related items to return 
        OUTPUT:
            items - List of the top n related item names

        For a given item find the n most similar items to it (this can be done using the similarity matrix created in the fit method)
        '''
        grouped_mine = pd.read_pickle('../pca_mine_no_cluster.pkl')
        grouped_all = pd.read_pickle('../pca_all_no_cluster.pkl')

        # Searches for song through Spotipy and then gets variables for the output
        song_df = get_song(song_name, artist_name)

        print(f'You chose {song_df.index[0][1]} by {song_df.index[0][2]} for your song', '\n')
        img = Image.open(requests.get(song_df.index[0][4], stream=True).raw)
        plt.imshow(img)
        plt.axis('off')
        plt.show()

        song_recs = song_df[self.item_counts.columns]

        simsim = cosine_similarity(song_recs, self.item_counts)

        recs_arr = np.argsort(simsim, axis=1)[0][-(n+1):-1]

        for idx, i in enumerate(recs_arr, start=1):
            ser = self.item_counts.iloc[[i], :]
            
            if idx == 1:
                df_recs = pd.DataFrame(ser)
                
            df_recs = df_recs.append(pd.DataFrame(ser))
        
        recs = df_recs.reset_index()
        
        print(f'The most similar {n} songs are displayed below:')
        
        fig = plt.figure(figsize=(10,14))
        ax = []
        columns = 4
        rows = math.ceil(n / columns)
        
        for i in range(n):
            # Captures image to be printed by MatPlotLib at the end of the loop
            img = Image.open(requests.get(recs['album_image_url'].values[i], stream=True).raw)
            ax.append(fig.add_subplot(rows, columns, i+1))
            title = (f'Song Name: {recs["name"][i]}\n Artist Name: {recs["artist"][i]}\n Album Name: {recs["album"][i]}')
            ax[-1].set_title(title, fontsize=8)
            ax[-1].set_axis_off()
            plt.imshow(img)
        
        
        plt.tight_layout()
        plt.show()

        artist_rec = max(Counter(recs['artist']).items(), key=operator.itemgetter(np.random.randint(1)))[0]

        print('\n', f'Artist Recommendation: {artist_rec}', '\n')
        
        plt.imshow(Image.open(requests.get(recs[recs['artist'] == artist_rec]['artist_image_url'].values[0], stream=True).raw))
        plt.axis('off')
        plt.show()

        # Recommending songs from my albums

        my_album_recs = song_df[grouped_mine.columns]

        groupsim = cosine_similarity(my_album_recs, grouped_mine)

        group_rec_arr = np.argsort(groupsim, axis=1)[0][-4:-1]

        for idx, i in enumerate(group_rec_arr, start=1):
            ser = grouped_mine.iloc[[i], :]
            
            if idx == 1:
                df_recs = pd.DataFrame(ser)
                
            df_recs = df_recs.append(pd.DataFrame(ser))
        
        group_recs = df_recs.reset_index()

        print(f"Meanwhile, while you're waiting for the new {artist_rec} album, you can try one of your own albums below:")

        fig = plt.figure(figsize=(10,14))
        ax = []
        columns = 4
        rows = 1

        for i in range(1,4):
            # Captures image to be printed by MatPlotLib at the end of the loop
            img = Image.open(requests.get(group_recs['album_image_url'].values[i], stream=True).raw)
            ax.append(fig.add_subplot(rows, columns, i+1))
            title = (f'Album Name: {group_recs["album"][i]}\nArtist Name: {group_recs["artist"][i]}')
            ax[-1].set_title(title, fontsize=8)
            ax[-1].set_axis_off()
            plt.imshow(img)


        plt.tight_layout()
        plt.show()

        # Recommending album from all albums

        all_album_recs = song_df[grouped_all.columns]

        groupsim = cosine_similarity(all_album_recs, grouped_all)

        group_rec_arr = np.argsort(groupsim, axis=1)[0][-4:-1]

        for idx, i in enumerate(group_rec_arr, start=1):
            group_ser = grouped_all.iloc[[i], :]
            
            if idx == 1:
                group_df_recs = pd.DataFrame(group_ser)
                
            group_df_recs = group_df_recs.append(pd.DataFrame(group_ser))
        
        group_recs = group_df_recs.reset_index()


        print(f"And if you're looking to purchase a new record for the collection, here are some good options:")

        fig = plt.figure(figsize=(10,14))
        ax = []
        columns = 4
        rows = 1

        for i in range(1,4):
            # Captures image to be printed by MatPlotLib at the end of the loop
            img = Image.open(requests.get(group_recs['index'][i][2], stream=True).raw)
            ax.append(fig.add_subplot(rows, columns, i+1))
            title = (f'Album Name: {group_recs["index"][i][0]}\nArtist Name: {group_recs["index"][i][1]}')
            ax[-1].set_title(title, fontsize=8)
            ax[-1].set_axis_off()
            plt.imshow(img)

        plt.tight_layout()
        plt.show()