import speech_recognition as sr

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy

"""
run with command, set env variables
export SPOTIPY_CLIENT_ID='xxx' && export SPOTIPY_CLIENT_SECRET='xxx' &&
export SPOTIPY_REDIRECT_URI='URL from spotify dashboard' && python detect.py
"""


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
            if token1[t1 - 1] == token2[t2 - 1]:
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if a <= b and a <= c:
                    distances[t1][t2] = a + 1
                elif b <= a and b <= c:
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    # printDistances(distances, len(token1), len(token2))
    return distances[len(token1)][len(token2)]


class SpotipyApp:
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
        "playlist-modify-private",
    ]
    sp = None
    recognizer = None
    microphone = None
    text = None

    def __init__(
        self,
    ):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.sp.volume(100)

        self.app_loop()

    def get_closest_title_url(self, items, title, artist=None):
        class reversor:
            def __init__(self, obj):
                self.obj = obj

            def __eq__(self, other):
                return other.obj == self.obj

            def __lt__(self, other):
                return other.obj < self.obj

        small_objects = list(
            map(
                lambda x: {
                    "popularity": x["popularity"],
                    "distance": levenshteinDistanceDP(x["name"], title),
                    "url": x["external_urls"]["spotify"],
                    "artists": list(map(lambda x: x["name"], x["artists"])),
                },
                items,
            )
        )
        small_objects.sort(key=lambda x: (x["distance"], reversor(x["popularity"])))
        if artist is not None:
            filtered_objects = list(
                filter(lambda x: artist in x["artists"], small_objects)
            )
            if len(filtered_objects) == 0:
                return small_objects[0]["url"]
            else:
                return filtered_objects[0]["url"]
        return small_objects[0]["url"]

    def handle_next_song(
        self,
    ):
        self.sp.next_track()

    def handle_set_volume(
        self,
    ):
        tokens = self.text.split(" ")
        for token in tokens:
            if "%" in token:
                number = int(token[:-1])
                self.sp.volume(number)
                break

    def handle_search_and_play(self):
        tokens = self.text.split(" ")

        idx = tokens.index("playing") + 1
        title = tokens[idx:]
        title = " ".join(title)

        print("title:", title)

        searchResults = self.sp.search(title, 10, 0, "track")
        tracks_dict = searchResults["tracks"]
        tracks_items = tracks_dict["items"]

        song_url = self.get_closest_title_url(tracks_items, title)

        self.sp.add_to_queue(song_url)
        self.sp.next_track()

    def handle_search_and_play_artist(
        self,
    ):
        tokens = self.text.split(" ")

        if "by the artist" in self.text:
            idx_end = tokens.index("by")
            idx_artist = tokens.index("artist") + 1

        idx = tokens.index("playing") + 1
        title = tokens[idx:idx_end]
        title = " ".join(title)

        artist = tokens[idx_artist:]
        artist = " ".join(artist)

        print("title:", title, "----", artist)

        searchResults = self.sp.search(title, 10, 0, "track")

        tracks_dict = searchResults["tracks"]
        tracks_items = tracks_dict["items"]

        song_url = self.get_closest_title_url(tracks_items, title, artist)

        self.sp.add_to_queue(song_url)
        self.sp.next_track()

    def handle_start(
        self,
    ):
        self.sp.start_playback()

    def handle_stop(
        self,
    ):
        self.sp.pause_playback()

    def app_loop(
        self,
    ):
        print("You can talk now")
        while True:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
            try:
                self.text = self.recognizer.recognize_google(audio)
                # self.text = "start playing The Girl From Ipanema by the artist Stan Getz"
                print(self.text)
                tokens = self.text.split(" ")

                if any(x in tokens for x in ["play", "start"]) and len(tokens) < 3:
                    self.handle_start()
                elif any(x in tokens for x in ["stop", "pause"]):
                    self.handle_stop()
                elif all(
                    x in tokens for x in ["start", "playing", "by", "the", "artist"]
                ):
                    self.handle_search_and_play_artist()
                elif all(
                    x in tokens
                    for x in [
                        "start",
                        "playing",
                    ]
                ):
                    self.handle_search_and_play()
                elif all(x in tokens for x in ["set", "volume", "to"]):
                    self.handle_set_volume()
                elif all(x in tokens for x in ["play", "next", "song"]):
                    self.handle_next_song()

            except sr.UnknownValueError:
                pass


if __name__ == "__main__":

    SpotipyApp()
