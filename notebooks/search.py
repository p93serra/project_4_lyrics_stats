import requests
import urllib.request
import urllib.parse
import json
from bs4 import BeautifulSoup

base = "https://api.genius.com"

path_cred = "/Users/pauserrabergeron/Private/Ironhack/Course/credentials/"
f = open(path_cred + "genius_credentials.txt", "r")
dict_credentials = json.loads(f.read()[:-1])

def get_json(path, params=None, headers=None):
    '''Send request and get response in json format.'''

    # Generate request URL
    requrl = '/'.join([base, path])
    token = "Bearer {}".format(dict_credentials["client_id"])
    if headers:
        headers['Authorization'] = token
    else:
        headers = {"Authorization": token}

    # Get response object from querying genius api
    response = requests.get(url=requrl, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def search(artist_name):
    '''Search Genius API via artist name.'''
    search = "search?q="
    query = base + search + urllib.parse.quote(artist_name)
    request = urllib.request.Request(query)

    request.add_header("Authorization", "Bearer " + dict_credentials["client_id"])
    request.add_header("User-Agent", "")

    response = urllib.request.urlopen(request, timeout=3)
    raw = response.read()
    data = json.loads(raw)['response']['hits']

    for item in data:
        # Print the artist and title of each result
        print(item['result']['primary_artist']['name']
              + ': ' + item['result']['title'])


def search_artist(artist_id):
    '''Search meta data about artist Genius API via Artist ID.'''
    search = "artists/"
    path = search + str(artist_id)
    request = get_json(path)
    data = request['response']['artist']

    print(data["followers_count"])
    # Lots of information we can scrape regarding the artist, check keys
    return data["followers_count"] # number of followers
