import click
import json
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

with open("config.json", "r") as configfile:
    obj = json.load(configfile)
    apikey, url = obj["apikey"], obj["url"]

@click.command()
@click.argument("audio_filepath",
                required=True,
                type=click.Path(exists=True))
def cli(audio_filepath):
    click.echo(_transcribe_sync(audio_filepath))

def _transcribe_sync(audio_filepath):
    with open(audio_filepath, "rb") as audiofile:
        authenticator = IAMAuthenticator(apikey)
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_service_url(url)
        response = speech_to_text.recognize(audiofile)
        return response
