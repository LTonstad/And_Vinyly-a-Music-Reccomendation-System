# DSI_Capstone_Three

## Music Album Content Based Recommender

* Would idealy like to feed album or playlist to get features of the songs and have it recommend another album based on the similarities in song data gathered through [Spotipy](https://spotipy.readthedocs.io/en/2.18.0/#examples)

* Could get a users already owned/wanted albums through [Discogs API](https://www.discogs.com/developers)
  * Tested this and able to get Albums from userID

Get Album id's --> https://stackoverflow.com/questions/36237522/get-spotipy-album-id-from-album


Columns that I'd want in csv:

```python
* ['name', 'album', 'year', 'artist', 'featured_artists', 'track_number',
       'tracks_on_album', 'explicit', 'duration_ms', 'popularity',
       'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
       'type', 'id', 'uri', 'track_href', 'analysis_url', 'time_signature',
       'artist_uri', 'album_uri', 'release_date', 'album_image_url',
       'track_length', 'tempo_confidence', 'end_fade_in', 'start_fade_out',
       'end_silence_time', 'sections', 'tatums', 'beats', 'bars']
```

# Steps to be taken

## Decisions to be made

* **Completed**Setup AWS
* What to choose for Feature Engineering & Recommender Model
* What pool of music to have Recommender system choose from
    * Chose [Rolling Stones top 100 albums](https://www.besteveralbums.com/thechart.php?c=62479) & [1000 Best albums of 2010s](https://www.besteveralbums.com/yearstats.php?y=201&f=&fv=&orderby=InfoRankScore&sortdir=DESC&page=2)
    * Possibly have it recommend 1-3 for each
    * When running through the script to get this data through Spotipy, there was a handful that it was not able to find

## Getting Data through Spotipy

* **Completed** Pulling all of the songs from my albums along with 40 features of the songs within the albums
* Need to decide what to do with the huge 4 columns --> ['sections', 'tatums', 'beats', 'bars']

## Feature Engineering

* PCA/NMF

## Cluster Albums

* Probably use K-Means

## Create Model

* Sequential Neural Network

## Setup recommender for presentation

* Probably Flask