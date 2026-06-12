from fastapi import APIRouter, UploadFile, File, Depends
from typing import Dict, Any
from ..agents.payroll import PayrollAgent
from ..api.auth import get_current_user_email

router = APIRouter(prefix="/payroll", tags=["payroll"])

@router.post("/upload")
async def process_payroll(
    file: UploadFile = File(...),
    email: str = Depends(get_current_user_email)
):
    """
    Processes a payroll CSV and returns suggested journal entries.
    """
    agent = PayrollAgent()
    content = await file.read()

    payroll_data = await agent.process_payroll_file(content.decode("utf-8"))
    journal_entry = agent.generate_journal_entry(payroll_data)

    return {
        "status": "success",
        "payroll_summary": payroll_data,
        "suggested_journal_entry": journal_entry
    }
