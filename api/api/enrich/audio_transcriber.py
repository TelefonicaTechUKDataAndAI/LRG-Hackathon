import os
import azure.cognitiveservices.speech as speechsdk


class AudioTranscriber:
    def __init__(self) -> None:
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("SPEECH_KEY"),
            region=os.environ.get("SPEECH_REGION"),
        )

        self.speech_config.speech_recognition_language = "en-US"

    def transcribe_from_stream(self, stream):
        audio_stream = speechsdk.audio.PushAudioInputStream(
            stream_format=speechsdk.audio.AudioStreamFormat()
        )

        audio_stream.write(stream.read())
        stream.seek(0)
        audio_stream.close()
        stream.truncate(0)

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        auto_detect_source_language_config = (
            speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=["en-US", "fr-FR", "es-ES"]
            )
        )

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config,
        )

        result = speech_recognizer.recognize_once()

        return result.text
