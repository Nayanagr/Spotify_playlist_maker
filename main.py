"""It takes some time to process about 30 seconds, but it is way faster than the approach a normal human will take to
make a playlist from a billboard."""
import os

import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

# ---------------------------------------------------CONSTANTS-----------------------------------------------------#

CLIENT_ID = os.getenv("Client ID")
CLIENT_SECRET = os.getenv("Client Secret")
REDIRECT_URL = "http://example.com"
USER_ID = os.getenv("USER ID")
#
# ---------------------------------------------------Setup SPOTIPY--------------------------------------------------#

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URL,
                        scope='playlist-modify-private')
token_info = sp_oauth.get_cached_token()
# Create a Spotipy object with the token
sp = spotipy.Spotify(auth=token_info["access_token"])

# -----------------------WEB SCRAPING AND DATA REFINING BASED ON USER INPUT--------------------------------------------#

date = input("Which year do you want to travel to? Type in YYYY-MM-DD format.")
YEAR = date[:4]

load = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/")
content = load.text

soup = BeautifulSoup(content, features="html.parser")
titles = soup.findAll("h3", {"id": "title-of-a-story", "class": "c-title a-no-trucate a-font-primary-bold-s "
                                                                "u-letter-spacing-0021 lrv-u-font-size-18@tablet "
                                                                "lrv-u-font-size-16 u-line-height-125 "
                                                                "u-line-height-normal@mobile-max a-truncate-ellipsis "
                                                                "u-max-width-330 u-max-width-230@tablet-only"})
top = soup.find("a", {"class": "c-title__link lrv-a-unstyle-link"})

top_text = top.getText().strip()
title_list = [top_text]

for i in titles:
    title_list.append(i.getText().strip())

# ----------------------------SEARCHING FOR SONGS ON SPOTIFY AND MAKING A LIST FROM IT----------------------------#

uri_list = []
for title in title_list:
    response = sp.search(q={f"track:{title} year: {YEAR}"}, limit=1, type="track")
    try:
        uri_list.append(response['tracks']['items'][0]['id'])
    except IndexError:
        print(f"Could not find the song {title}, 'SKIPPED' ")
        pass

playlist = sp.user_playlist_create(user=USER_ID, name=f'{date} Billboard 100',
                                   description="""This Playlist is made as part of the educational project for python 
                                   by Nayan Agrawal.""",
                                   public=False)

playlist_id = playlist['id']
sp.playlist_add_items(playlist_id=playlist_id, items=uri_list)
