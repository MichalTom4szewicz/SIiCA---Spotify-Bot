import speech_recognition as sr

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import numpy

"""
run with command, set env variables
export SPOTIPY_CLIENT_ID='xxx' && export SPOTIPY_CLIENT_SECRET='xxx' &&
export SPOTIPY_REDIRECT_URI='URL from spotify dashboard' && python detect.py
"""

scope = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-recently-played",
    "user-read-playback-position",
    "app-remote-control",
    "streaming",
    "playlist-modify-public",
    "user-library-modify",
    "user-read-currently-playing",
    "user-library-read",
    "playlist-modify-private"
]

def levenshteinDistanceDP(token1, token2):
    distances = numpy.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    a = 0
    b = 0
    c = 0

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1-1] == token2[t2-1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    # printDistances(distances, len(token1), len(token2))
    return distances[len(token1)][len(token2)]

class reversor:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
           return other.obj < self.obj

def get_closest_title_url(items, title, artist=None):

    if artist is None:
        mapped = list(map(lambda x: (x["popularity"], levenshteinDistanceDP(x["name"], title), x['external_urls']['spotify']), items))
        mapped.sort(key=lambda x: (x[1], reversor(x[0])))
        print(mapped)
        return mapped[0][2]
    else:
        mapped = list(map(lambda x: (x["popularity"], levenshteinDistanceDP(x["name"], title), x['external_urls']['spotify'], list(map(lambda x: x["name"], x["artists"]))), items))
        mapped.sort(key=lambda x: (x[1], reversor(x[0])))
        filtered = list(filter(lambda x: artist in x[3], mapped))
        if len(filtered) == 0:
            return mapped[0][2]
        print(filtered)
        return filtered[0][2]



if __name__ == "__main__":

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp.volume(100)
    print("You can talk now")

    while(True):
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            # text = "start playing The Girl From Ipanema by the artist Stan Getz"
            print(text)
            tokens = text.split(" ")


            if any(x in tokens for x in ["play", "start"]) and len(tokens) < 3:

                sp.start_playback()
            elif all(x in tokens for x in ["stop",]):

                sp.pause_playback()

            elif all(x in tokens for x in ["start", "playing", "by", "the", "artist"]):

                idx_end = 999
                if "by the artist" in text:
                    idx_end = tokens.index("by")
                    idx_artist = tokens.index("artist") + 1

                idx = tokens.index("playing") + 1
                title = tokens[idx:idx_end]
                title = " ".join(title)

                artist = tokens[idx_artist:]
                artist = " ".join(artist)

                print(title, "----" ,artist)

                searchResults = sp.search(title, 10, 0, "track")

                tracks_dict = searchResults['tracks']
                tracks_items = tracks_dict['items']

                song_url = get_closest_title_url(tracks_items, title, artist)

                sp.add_to_queue(song_url)
                sp.next_track()

            elif all(x in tokens for x in ["start", "playing",]):

                idx = tokens.index("playing") + 1
                title = tokens[idx:idx_end]
                title = " ".join(title)

                print("title:", title)

                searchResults = sp.search(title, 10, 0, "track")
                tracks_dict = searchResults['tracks']
                tracks_items = tracks_dict['items']

                song_url = get_closest_title_url(tracks_items, title)

                sp.add_to_queue(song_url)
                sp.next_track()

            elif all(x in tokens for x in ["set", "volume", "to"]):
                number = 100
                print("volumeee")

                for tok in tokens:
                   if "%" in tok:
                        number = int(tok[:-1])
                        sp.volume(number)
                        break
            elif all(x in tokens for x in ["play", "next", "song"]):
                sp.next_track()

            elif tokens == "99":
                searchResults = sp.search("Stan Getz The Girl From Ipanema", 10, 0, "track")
                # print(searchResults)
                y = json.dumps(searchResults)
                print(y)

        except sr.UnknownValueError:
            pass