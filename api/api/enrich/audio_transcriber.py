import os
import struct
from typing import BinaryIO
import azure.cognitiveservices.speech as speechsdk


class AudioTranscriber:
    def __init__(self) -> None:
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("SPEECH_KEY"),
            region=os.environ.get("SPEECH_REGION"),
        )

        self.speech_config.speech_recognition_language = "en-US"

    async def transcribe_from_stream(self, file_name):
        audio_config = speechsdk.audio.AudioConfig(filename=file_name)

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
        )

        result = speech_recognizer.recognize_once()

        return result.text
