import json
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

if __name__ == "__main__":
    with open("ibm.json", "r") as configfile:
        obj = json.load(configfile)
        apikey, url = obj["apikey"], obj["url"]

    with open("audio-file.flac", "rb") as audiofile:
        authenticator = IAMAuthenticator(apikey)
        speech_to_text = SpeechToTextV1(
            authenticator=authenticator
        )
        speech_to_text.set_service_url(url)
        response = speech_to_text.recognize(audiofile)
