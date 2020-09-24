import click
import os
import sys
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import DetailedResponse
from typing import Final, List
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
                '- Navigate to the directory where you saved the "ibm-credentials.env" file',
                '- Run this script again'
            ]
        )
    )

# defaults
MIN_WORD_CONFIDENCE: Final = 0.3


@click.command()
@click.option(
    "--word-confidence-cutoff",
    default=MIN_WORD_CONFIDENCE,
    show_default=True,
    type=click.FloatRange(min=0, max=1.0),
    help=f"The minimum word confidence level to accept into a transcript. Value should be in the range 0.0 to 1.0.",
)
@click.argument("path_to_audio_file", required=True, type=click.Path(exists=True))
def cli(path_to_audio_file: str, word_confidence_cutoff: float):
    response = transcribe_sync(path_to_audio_file)
    filename, _ = os.path.splitext(os.path.basename(path_to_audio_file))
    with open(f"{filename}.json", "w") as response_outfile:
        response_outfile.write(str(response))
    click.echo(f'Raw response data written to "{filename}.json"')
    transcript = combine_transcriptions(response, word_confidence_cutoff)
    with open(f"{filename}.txt", "w") as transcript_outfile:
        transcript_outfile.write(transcript)
    click.echo(f'Transcript written to "{filename}.txt"')


def transcribe_sync(audio_filepath: str) -> DetailedResponse:
    with open(audio_filepath, "rb") as audiofile:
        authenticator = IAMAuthenticator(APIKEY)
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_default_headers({"X-Watson-Learning-Opt-Out": "true"})
        speech_to_text.set_service_url(APIURL)
        click.echo("Transcribing audio, this may take a while...")
        response = speech_to_text.recognize(
            audiofile,
            word_confidence=True,
            end_of_phrase_silence_time=30.0,
            profanity_filter=False,
        )
        return response


def combine_transcriptions(
    response: DetailedResponse, word_confidence_cutoff: float
) -> str:
    """Combine transcription segments into a single transcription."""
    transcripts: List[str] = []
    for result in response.result["results"]:
        confident_words = [
            word_item[0]
            for word_item in result["alternatives"][0]["word_confidence"]
            if word_item[1] >= word_confidence_cutoff and word_item[0] != "%HESITATION"
        ]
        transcripts.append(" ".join(confident_words))
    return "\n".join(transcripts)
