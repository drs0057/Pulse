import json
import string
from base64 import b64encode
from random import choice
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv
import os

load_dotenv()
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = "http://127.0.0.1:8000/play"
auth_string = client_id + ':' + client_secret
auth_bytes = auth_string.encode("utf-8")
auth_base64 = str(b64encode(auth_bytes), "utf-8")

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(choice(letters_and_digits) for _ in range(length))
    return random_string


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def user_access_url():
    url = 'https://accounts.spotify.com/authorize?'
    data = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'state': generate_random_string(16),
        'scope': 'user-library-read streaming user-read-email user-read-private',
        'show_dialog': True
    }
    user_access_url = url + urlencode(data)
    return user_access_url


def request_access_refresh_token(code):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
        }
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    try:
        access_token = json_result["access_token"]
        refresh_token = json_result["refresh_token"] 
    except KeyError:
        return None, None
    return access_token, refresh_token


def request_gamedata_images(gamedata, token):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    # Artist
    query = f"?q={gamedata['fastest_artist'][0]}&type=artist"
    result = requests.get(url + query, headers=headers)
    json_result = json.loads(result.content)
    artist_url = json_result['artists']['items'][0]['images'][0]['url']
    # Album
    query = f"?q={gamedata['fastest_album'][0]}&type=album"
    result = requests.get(url + query, headers=headers)
    json_result = json.loads(result.content)
    album_url = json_result['albums']['items'][0]['images'][0]['url']
    # Song will take the artist's image
    query = f"?q={gamedata['fastest_song'][0]}&type=track"
    result = requests.get(url + query, headers=headers)
    json_result = json.loads(result.content)
    song_artist = json_result['tracks']['items'][0]['artists'][0]['name']
    query = f"?q={song_artist}&type=artist"
    result = requests.get(url + query, headers=headers)
    json_result = json.loads(result.content)
    song_artist_url = json_result['artists']['items'][0]['images'][0]['url']

    image_uris = {
        "artist_url": artist_url,
        "album_url": album_url,
        "song_artist_url": song_artist_url,
        "song_artist_name": song_artist
    }
    return image_uris


def request_refreshed_access_token(refresh_token):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    refreshed_access_token = json_result["access_token"]
    return refreshed_access_token


def request_user_songs(token, offset, limit, songs):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = get_auth_header(token)
    query = f"?market=US&offset={offset}&limit={limit}"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    items = json_result["items"]
    for item in items:
        songs.append({
            'name': item["track"]["name"], 
            'artist': item["track"]["artists"][0]["name"],
            'uri': item["track"]["uri"],
            'image_url': item["track"]["album"]["images"][0]["url"]
        })
    return songs


def songs_by_artist(songs, artist):
    songs_by_artist = []
    for song in songs:
        if song["artist"] == artist:
            songs_by_artist.append(song["name"])
    return songs_by_artist


def request_song_info(song_uri, token):
    SpotifyId = song_uri[14:]
    url = f'https://api.spotify.com/v1/tracks/{SpotifyId}'
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    albumName = json_result['album']['name']
    artistName = json_result['artists'][0]['name']
    songName = json_result['name']
    return albumName, artistName, songName


def request_user_info(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result["images"][0]["url"], json_result["display_name"]


def request_user_library_size(token):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = get_auth_header(token)
    query = f"?market=US&offset=0&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    library_size = json_result["total"]
    return library_size


# def search_for_artist(token, artist_name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     query = f"?q={artist_name}&type=artist&limit=1"
#     query_url = url + query
#     result = requests.get(query_url, headers=headers)
#     json_result = json.loads(result.content)
#     return(json_result)

# token = get_token()
# result = search_for_artist(token, 'John Mayer')
# print(json.dumps(result, indent=4))
# print(result["artists"]["items"][0]["name"])