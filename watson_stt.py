import click
import json
import os
import sys
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from typing import Final
from dotenv import load_dotenv

load_dotenv("ibm-credentials.env")
APIKEY: Final = os.getenv("SPEECH_TO_TEXT_APIKEY")
APIURL: Final = os.getenv("SPEECH_TO_TEXT_URL")
if not APIKEY or not APIURL:
    sys.exit(
        "\n".join(
            [
                "[Error] The Watson API key and/or URL are not defined. To fix this:",
                '- Navigate to "https://cloud.ibm.com/resources" (logging in if needed)',
                '- Under "Services", select your "Speech to Text" service instance',
                '- Click "View Full Details"',
                '- In the "Credentials" pane, click "Download"',
                '- Place the "ibm-credentials.env" file in the same directory as this script, then try again',
            ]
        )
    )


@click.command()
@click.argument("path_to_audio_file", required=True, type=click.Path(exists=True))
def cli(audio_filepath: str):
    click.echo(_transcribe_sync(audio_filepath))


def _transcribe_sync(audio_filepath):
    with open(audio_filepath, "rb") as audiofile:
        authenticator = IAMAuthenticator(APIKEY)
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_service_url(APIURL)
        response = speech_to_text.recognize(
            audiofile, word_confidence=True, end_of_phrase_silence_time=30.0
        )
        return response


def combine_transcriptions(json_object):
    transcripts = map(
        lambda x: x["alternatives"][0]["transcript"], json_object["results"]
    )
    return "\n".join(transcripts)


def get_transcript(filepath):
    response = _transcribe_sync(filepath)
    json_filepath = filepath.replace(".opus", ".json")
    txt_filepath = filepath.replace(".opus", ".txt")
    with open(json_filepath, "w") as json_outfile:
        json.dump(response.result, json_outfile, indent=4)
    transcript = combine_transcriptions(response.result)
    with open(txt_filepath, "w") as txt_outfile:
        txt_outfile.write(transcript)
