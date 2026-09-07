from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: datetime = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    status: str  # approved, failed, processing
    details: Optional[Dict[str, Any]] = None