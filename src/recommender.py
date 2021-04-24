from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, MinMax
from src.get_data import *
import pandas as pd
import numpy as np

class ItemRecommender():
    '''
    Content based item recommender
    '''
    def __init__(self, similarity_measure=cosine_similarity):
        self.similarity_matrix = None
        self.item_names = None
        self.similarity_measure = similarity_measure

    
    def fit(self, X, titles=None):
        '''
        Takes a numpy array of the item attributes and creates the similarity matrix

        INPUT -
            X: NUMPY ARRAY - Rows are items, columns are feature values / or DF
            titles: LIST - List of the item names/titles in order of the numpy arrray
        
        OUTPUT - None


        Notes:  You might want to keep titles and X as attributes to refer to them later

        Create a similarity matrix of item to item similarity
        '''

        # While keeping this as a sparse matrix would be best the cosign sim
        # function returns a array so there is no reason.

        lst_of_albums = X.index.get_level_values(1)

        scaler = StandardScaler()
        scale_matrix = scaler.fit_transform(X)

        indices = pd.Series(lst_of_albums)

        count_df = pd.DataFrame(scale_matrix, index=indices.values)

        print(count_df)

        self.item_counts = X
        self.item_names = X.index
        self.similarity_df = pd.DataFrame(self.similarity_measure(count_df.values, count_df.values),
                index = self.item_names)

        
    def get_recommendations(self, song_name, artist_name, n=5):
        '''
        Returns the top n items related to the item passed in
        INPUT:
            item    - STRING - Name of item in the original DataFrame 
            n       - INT    - Number of top related items to return 
        OUTPUT:
            items - List of the top n related item names

        For a given item find the n most similar items to it (this can be done using the similarity matrix created in the fit method)
        '''
        # Searches for song through Spotipy and then gets variables for the output
        song_df = get_song(song_name, artist_name)

        print(f'You chose {song_df.index[0][1]} for your song', '\n')
        img = Image.open(requests.get(song_df.index[0][4], stream=True).raw)
        plt.imshow(img)
        plt.show()
        
        simsim = cosine_similarity(song_df, self.item_counts)

        recs_arr = np.argsort(simsim, axis=1)[0][-(n+1):-1]

        for idx, i in enumerate(recs_arr, start=1):
            ser = self.item_counts.iloc[[i], :]
            
            print('\n', f'Number {idx} pick:', '\n')
            if idx == 1:
                df_recs = pd.DataFrame(ser)
                
            print('\n', f'Song chosen: {ser.index[0][1]}', '\n', 
                f'Performed by: {ser.index[0][2]}', 
                '\n', f'On the Album: {ser.index[0][0]}', '\n')
            
            # Captures image to be printed by MatPlotLib at the end of the loop
            img = Image.open(requests.get(ser.index[0][4], stream=True).raw)
            
            plt.imshow(img)
            plt.show()
            
            df_recs = df_recs.append(pd.DataFrame(ser))

        return df_recs



