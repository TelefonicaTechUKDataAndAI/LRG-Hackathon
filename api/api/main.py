import os
import json
import tempfile
import dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from typing import Any
from fastapi import File, UploadFile

from api.chat.chat_handler import AgentChatHandler
from api.enrich.doc_processor import DocumentProcessor
from api.search.sql_handler import AzureSQLConnector

dotenv.load_dotenv()

app = FastAPI()
agent_handler = AgentChatHandler()
doc_processor = DocumentProcessor()

class ProcessRequest(BaseModel):
    body: str

class FetchRecordRequest(BaseModel):
    personId: int

class LogChatRequest(BaseModel):
    personId: int
    messages: list[dict[str, str]] 

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

@app.post(path="/api/fetch_record")
async def fetch_record(request: FetchRecordRequest) -> ProcessResponse:

    try:
        with AzureSQLConnector() as db:
            result = db.query_by_id(request.personId)
            parsed_result = json.loads(result)
            return ProcessResponse(response=f"✅ Record found: {parsed_result[0].get('name', 'N/A')}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from database connector: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post(path="/api/log_chat")
async def log_chat(request: LogChatRequest) -> ProcessResponse:

    try:
        with AzureSQLConnector() as db:
            for message in request.messages:
                db.execute_insert(
                    "INSERT INTO dbo.Logs (person_id, role, message) VALUES (?, ?, ?)",
                    (request.personId, message["role"], message["message"])
                )
            return ProcessResponse(response="✅ Chat log saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))