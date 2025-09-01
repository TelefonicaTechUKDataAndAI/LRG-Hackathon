import os
import tempfile
import dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from typing import Dict
from fastapi import File, UploadFile

from api.chat.chat_handler import ChatHandler, AgentChatHandler
from api.enrich.doc_processor import DocumentProcessor

dotenv.load_dotenv()

app = FastAPI()

chat_handler = ChatHandler()
agent_handler = AgentChatHandler()
doc_processor = DocumentProcessor()

class ProcessRequest(BaseModel):
    body: str
class ProcessResponse(BaseModel):
    response: str

uploaded_files = []

@app.post("/api/process")
async def process(request: ProcessRequest) -> ProcessResponse:
    response_content = str(agent_handler.get_agentic_chat_response(request.body))
    return ProcessResponse(response=response_content)

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
        response_content = agent_handler.get_agentic_redaction_response(file)
        redacted_texts.append(response_content)

    output = " ".join(redacted_texts)
    return ProcessResponse(response=output)
