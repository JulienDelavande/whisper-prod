import argparse
import requests

def transcribe(endpoint_url, audio_file):
    with open(audio_file, "rb") as f:
        files = {"file": f.read()}
        response = requests.post(endpoint_url, files=files)
        response.raise_for_status()
        print("📝 Transcript:", response.json()["text"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Whisper transcription endpoint.")
    parser.add_argument(
        "--endpoint",
        type=str,
        default="http://localhost:8000/v1/audio/transcriptions",
        help="URL of the Whisper transcription endpoint.",
    )
    parser.add_argument(
        "--audio",
        type=str,
        default="audio/bonjour.m4a",
        help="Path to the audio file to transcribe.",
    )

    args = parser.parse_args()
    transcribe(args.endpoint, args.audio)
