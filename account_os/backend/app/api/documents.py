from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from typing import List, Dict, Any, Optional
import uuid
import os
from ..agents.orchestrator import Orchestrator

router = APIRouter(prefix="/documents", tags=["documents"])

# Mock DB storage for uploaded documents
uploaded_docs = {}

from .auth import get_current_user_email

@router.post("/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    platform: str = "qbo",
    entity_id: Optional[str] = None,
    email: str = Depends(get_current_user_email)
):
    """
    Receives multiple documents, saves them, and triggers the AI orchestration.
    """
    job_id = str(uuid.uuid4())
    results = []

    for file in files:
        file_id = str(uuid.uuid4())
        content = await file.read()

        # Save file metadata
        uploaded_docs[file_id] = {
            "filename": file.filename,
            "status": "uploaded",
            "email": email,
            "platform": platform,
            "entity_id": entity_id
        }

        # Handle PDF/Binary vs Text (Basic logic for MVP)
        # In production, use Textract/OCR here
        try:
            if file.content_type == "application/pdf":
                text_content = f"[PDF Document: {file.filename}] Content extracted via OCR mock."
            else:
                text_content = content.decode("utf-8")
        except:
            text_content = f"[Binary Document: {file.filename}] Content extracted via mock."

        # Trigger processing in background
        background_tasks.add_task(process_document_task, file_id, text_content, email, platform, entity_id)

        # Ensure metadata is updated to processing if started via background task
        uploaded_docs[file_id]["status"] = "queued"

        results.append({"file_id": file_id, "filename": file.filename})

    return {"job_id": job_id, "documents": results}

@router.get("/status/{file_id}")
async def get_document_status(file_id: str):
    if file_id not in uploaded_docs:
        raise HTTPException(status_code=404, detail="Document not found")
    return uploaded_docs[file_id]

from ..db.database import get_db_context
from sqlalchemy import text
from datetime import datetime

async def process_document_task(file_id: str, content_text: str, user_email: str, platform: str, entity_id: Optional[str] = None):
    """
    Background task to run the agentic workflow.
    """
    print(f"Starting process_document_task for {file_id}")
    uploaded_docs[file_id]["status"] = "processing"

    orchestrator = Orchestrator()

    # Resolve client_id from email
    async with get_db_context() as db:
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": user_email})
        client_id = res.scalar_one()

    initial_state = {
        "raw_text": content_text,
        "client_id": str(client_id),
        "entity_id": entity_id,
        "platform": platform,
        "chart_of_accounts": [], # Fetch from DB in production
        "rules": [],             # Fetch from DB in production
        "messages": [],
        "status": "started",
        "next_agent": "intake",
        "transaction_data": {}
    }

    try:
        print(f"Running orchestrator for {file_id}")
        final_state = await orchestrator.run(initial_state)
        print(f"Final state type: {type(final_state)}")
        print(f"Final state: {final_state}")
        print(f"Orchestrator finished for {file_id} with status {final_state.get('status')}")
        uploaded_docs[file_id]["status"] = final_state.get("status", "completed")
        tx_data = final_state.get("transaction_data", {})
        uploaded_docs[file_id]["transaction_data"] = tx_data

        # PERSIST TO DB
        async with get_db_context() as db:
            await db.execute(
                text("INSERT INTO transactions (id, client_id, entity_id, vendor_name, amount, currency, transaction_date, status, gl_code) VALUES (:id, :client_id, :entity_id, :vendor, :amount, :currency, :date, :status, :gl)"),
                {
                    "id": file_id,
                    "client_id": client_id,
                    "entity_id": entity_id,
                    "vendor": tx_data.get("vendor_name"),
                    "amount": tx_data.get("amount"),
                    "currency": tx_data.get("currency", "USD"),
                    "date": datetime.strptime(tx_data.get("transaction_date"), "%Y-%m-%d").date() if isinstance(tx_data.get("transaction_date"), str) else tx_data.get("transaction_date"),
                    "status": final_state.get("status"),
                    "gl": tx_data.get("gl_code")
                }
            )
            await db.commit()
            print(f"Transaction {file_id} persisted to DB.")

    except Exception as e:
        print(f"Error processing {file_id}: {e}")
        uploaded_docs[file_id]["status"] = "error"
        uploaded_docs[file_id]["error"] = str(e)
