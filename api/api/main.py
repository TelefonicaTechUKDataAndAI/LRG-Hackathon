import os
import json
import tempfile
import dotenv
import re
from datetime import datetime
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
all_annotations = []

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
            return ProcessResponse(response=f"✅ Record found: {parsed_result[0].get('FULL_NAME', 'N/A')}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from database connector: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post(path="/api/log_chat")
async def log_chat(request: LogChatRequest) -> ProcessResponse:
    ts = datetime.now().timestamp()
    try:
        with AzureSQLConnector() as db:
            for message in request.messages:                
                db.execute_insert(
                    "INSERT INTO dbo.Logs (person_id, session_id, role, message) VALUES (?, ?, ?, ?)",
                    (request.personId, ts,  message["role"], message["message"])
                )
                if message["role"] == "bot": 
                    pattern = r":\s*(.+)"
                    matches = re.findall(pattern, message["message"])
                    for match in matches: 
                        db.execute_insert(
                            "INSERT INTO dbo.service_logs (session_id, url) VALUES (?, ?)",
                            (ts, match.strip())
                        )
            #full_convo = " ".join([m.message for message in request.messages])
            log_extract = json.loads(agent_handler.get_agentic_kpi_response())
            db.execute_insert(
                    "INSERT INTO dbo.Kpi_Logs (session_id, category, service_support_area, nature_of_enquiry, information_or_advice_provided, outcome_or_next_steps, risk_flag, confidence ) VALUES (?, ?, ?, ?,?,?,?,?)",
                    (ts,  
                     log_extract["category"], 
                     log_extract["service_support_area"],
                     log_extract["nature_of_enquiry"],
                     log_extract["information_or_advice_provided"],
                     log_extract["outcome_or_next_steps"],
                     log_extract["risk_flag"],
                     log_extract["confidence"]
                     )
                )                       

            return ProcessResponse(response="✅ Chat log saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))