from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    INGESTED = "ingested"
    CODED = "coded"
    PENDING_APPROVAL = "pending_approval"
    READY_TO_SYNC = "ready_to_sync"
    SYNCED = "synced"
    REJECTED = "rejected"

class TransactionBase(BaseModel):
    vendor_name: str
    amount: float
    currency: str = "USD"
    transaction_date: Optional[date] = None
    document_type: str = "bill"

class TransactionCreate(TransactionBase):
    client_id: str
    entity_id: Optional[str] = None

class Transaction(TransactionBase):
    id: str
    status: TransactionStatus
    gl_code: Optional[str] = None
    approval_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class User(UserBase):
    id: str
    client_id: str
    is_active: bool

class SyncResponse(BaseModel):
    status: str
    platform: str
    external_id: Optional[str] = None
    message: Optional[str] = None
