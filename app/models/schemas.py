from pydantic import BaseModel, Field
from typing import List, Optional

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    text_preview: str

class ChatRequest(BaseModel):
    session_id: str
    query: str
    top_k: Optional[int] = Field(3, ge=1, le=50)

class StreamChunk(BaseModel):
    token: str
    done: bool = False
    step: Optional[str] = None
