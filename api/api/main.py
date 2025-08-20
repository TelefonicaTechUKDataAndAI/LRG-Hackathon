import os
import tempfile
import dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from typing import Dict
from fastapi import File, UploadFile

from api.chat.chat_handler import ChatHandler, AgentChatHandler
from api.enrich.doc_processor import DocumentProcessor
#from api.enrich.audio_converter import AudioConverter
#from api.enrich.audio_transcriber import AudioTranscriber

dotenv.load_dotenv()

app = FastAPI()

chat_handler = ChatHandler()
agent_handler = AgentChatHandler()
doc_processor = DocumentProcessor()
#audio_transcriber = AudioTranscriber()

class ProcessRequest(BaseModel):
    body: str
class ProcessResponse(BaseModel):
    response: str

uploaded_files = []

@app.post("/api/process")
async def process(request: ProcessRequest) -> ProcessResponse:
    response_content = str(chat_handler.get_chat_response(request.body).content)
    return ProcessResponse(response=response_content)

@app.post(path="/api/process-audit-file")
async def process_audit_file(request: UploadFile) -> ProcessResponse:
    # write the audit file to disk
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    file_ext = request.filename.split(".")[-1].lower()

    try:
        temp_file.write(await request.read())
        temp_file.close()

        # Process the audit file
        DocumentProcessor.extract_audit_text(temp_file.name, file_ext)

        # Return a success response
        return ProcessResponse(response="Audit file processed successfully ✅")
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
    
    return True

@app.post(path="/api/process-files")
async def process_doc_file(files: list[UploadFile] = File(...)) -> ProcessResponse:
    # List all file names received
    try:
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_ext = file.filename.split(".")[-1].lower()
            temp_file.write(await file.read())
            temp_file.close()

            # Extract text from the document
            processed_file = DocumentProcessor.extract_document_text(temp_file.name, file_ext)
            uploaded_files.append(processed_file)

        file_names = [file.filename for file in files]        
        return ProcessResponse(response="✅ Received files:\n\n" + ", ".join(file_names))
    
    except Exception as e:
        return ProcessResponse(response=f"Error processing files: {e}")
    
    finally:
        for file in files:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

@app.post(path="/api/redact-text")
async def redact_text() -> ProcessResponse:
    redacted_texts = []
    for file in uploaded_files:

        # Get the redacted response from the agentic chat handler
        response_content = agent_handler.get_agentic_chat_response(file)
        redacted_texts.append(response_content)

    output = " ".join(redacted_texts)
    return ProcessResponse(response=output)

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
