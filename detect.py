import speech_recognition as sr

import spotipy
from spotipy.oauth2 import SpotifyOAuth

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


if __name__ == "__main__":

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    print("You can talk now")

    while(True):
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(text)
            tokens = text.split(" ")

            if all(x in tokens for x in ["play", "computer"]):
                print("triggered")
                print(sp.devices()["devices"])

                id = [dev["id"] for dev in sp.devices()["devices"] if dev["type"] == "Computer"][0]
                sp.start_playback(device_id=id)
            elif all(x in tokens for x in ["play", "smartphone"]):
                print("triggered")
                print(sp.devices()["devices"])

                id = [dev["id"] for dev in sp.devices()["devices"] if dev["type"] == "Smartphone"][0]
                sp.start_playback(device_id=id)
            elif "play" in tokens:
                print("triggered")
                print(sp.devices()["devices"])
                sp.start_playback()
            elif all(x in tokens for x in ["stop", "computer"]):
                print("triggered")
                print(sp.devices()["devices"])

                id = [dev["id"] for dev in sp.devices()["devices"] if dev["type"] == "Computer"][0]
                print(id)
                sp.pause_playback(device_id=id)
            elif all(x in tokens for x in ["stop", "smartphone"]):
                print("triggered")
                print(sp.devices()["devices"])

                id = [dev["id"] for dev in sp.devices()["devices"] if dev["type"] == "Smartphone"][0]
                sp.pause_playback(device_id=id)
            elif "stop" in tokens:
                sp.pause_playback()


        except sr.UnknownValueError:
            pass