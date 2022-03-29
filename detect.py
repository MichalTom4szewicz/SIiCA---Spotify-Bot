import speech_recognition as sr

if __name__ == "__main__":

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("You can talk now")

    while(True):
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            tekst = recognizer.recognize_google(audio)
            print(tekst)
        except sr.UnknownValueError:
            pass