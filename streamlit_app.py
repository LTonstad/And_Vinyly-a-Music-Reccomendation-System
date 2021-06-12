from src.recommender import *
import streamlit as st

st.title("Welcome to And Vinyl'ly")

song_input = st.text_input('Song: ')
artist_input = st.text_input('Artist: ')
number_input = st.number_input('Number of Songs to return: ')

if st.button('Get Recommendations'):
    st.pyplot(ItemRecommender().fit(df_mega_main).get_recommendations(song_input, artist_input, n=number_input))