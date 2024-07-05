import dotenv
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from api.chat.chat_handler import ChatHandler
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
    # Transcribe audio
    transcribed_audio = audio_transcriber.transcribe_from_stream(request.file)

    # Send to chat handler
    response_content = str(chat_handler.get_chat_response(transcribed_audio).content)

    return ProcessResponse(response=response_content)
