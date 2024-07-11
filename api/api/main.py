import os
import tempfile
import dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

from api.chat.chat_handler import ChatHandler
from api.enrich.audio_converter import AudioConverter
from api.enrich.audio_transcriber import AudioTranscriber

dotenv.load_dotenv()

app = FastAPI()

chat_handler = ChatHandler()
audio_transcriber = AudioTranscriber()


class ProcessRequest(BaseModel):
    body: str


class ProcessResponse(BaseModel):
    response: str


@app.post("/api/process")
async def process(request: ProcessRequest) -> ProcessResponse:
    response_content = str(chat_handler.get_chat_response(request.body).content)
    return ProcessResponse(response=response_content)


@app.post(path="/api/process-audio-file")
async def process_audio_file(request: UploadFile) -> ProcessResponse:
    # Write the audio file to disk
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    try:
        temp_file.write(await request.read())
        temp_file.close()
      
        if request.content_type:
            if "webm" in request.content_type:
                temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

                # Convert webm to wav
                AudioConverter.convert_webm_to_wav(temp_file.name, temp_wav_file.name)

                temp_file = temp_wav_file

        # Transcribe audio
        transcribed_audio = await audio_transcriber.transcribe_from_file(
            temp_file.name
        )

        if len(transcribed_audio) == 0:
            raise HTTPException(
                status_code=400, detail="No audio content found in uploaded file"
            )

        # Send to chat handler
        response_content = str(
            chat_handler.get_chat_response(transcribed_audio).content
        )

        return ProcessResponse(response=response_content)
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
