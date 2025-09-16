import requests
import os
from dotenv import load_dotenv

token = None

def generate_bearer():
    body_data = {
        "grant_type":"client_credentials",
        "client_id":os.getenv('SPOTIFY_CLIENT_ID'),
        "client_secret":os.getenv('SPOTIFY_CLIENT_SECRET')
    }
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data = body_data,
        verify=False
     )
    access_token = response.json()['access_token']
    return access_token

def get_artist_id(artist_name):
    print(token)
    headers = {"Authorization":f"Bearer {token}"}
    response = requests.get(f'https://api.spotify.com/v1/search?q=artist:{artist_name}&type=artist', headers=headers).json()
    return response['artists']['items'][0]['id'] #retrieve ID

def get_top_tracks(artist_id):
    headers = {"Authorization":f"Bearer {token}"}
    response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks', headers=headers).json()
    tracks = []
    for track in response['tracks']:
        tracks.append(
            {
                'name':track['name'],
                'id':track['id'],
                'artist':track['artists'][0]['name']
            }
        )
    return tracks

def get_lyrics(artist_name, song_name):
    response = requests.get(f'https://api.lyrics.ovh/v1/{artist_name}/{song_name}')
    status_code = response.status_code
    if(status_code==404):
        return 'Song not found'
    elif status_code==200:
        return response.json()['lyrics']

def generate_top_tracks_lyrics(artist_name):
    artist_id = get_artist_id(artist_name)
    top_tracks = get_top_tracks(artist_id)
    lyrics = []
    for track in top_tracks:
        lyrics.append(
            {
            'metadata':track,
            'lyrics':get_lyrics(artist_name,track['name'])
            }
        )

    return lyrics
load_dotenv()
token = generate_bearer()
