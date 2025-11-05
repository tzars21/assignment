import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.config import settings
from app.parsing.pdf_parser import parse_pdf_bytes, PDFParseError, ParsedDocument
from app.agent.agno_agent import AgnoAgent, AgentConfig
from app.models.schemas import UploadResponse, ChatRequest
import asyncio
from typing import AsyncGenerator

app = FastAPI(title="RAG Chatbot - FastAPI + Agno")

DOCUMENT_STORE: dict[str, ParsedDocument] = {}
AGENTS: dict[str, AgnoAgent] = {}

def get_agent() -> AgnoAgent:
    if "default" not in AGENTS:
        cfg = AgentConfig()
        AGENTS["default"] = AgnoAgent(cfg)
    return AGENTS["default"]

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    document_id = str(uuid.uuid4())
    try:
        parsed = parse_pdf_bytes(contents, filename=file.filename, document_id=document_id)
        DOCUMENT_STORE[document_id] = parsed
        preview = (parsed.text[:500] + "...") if len(parsed.text) > 500 else parsed.text
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            pages=parsed.pages,
            text_preview=preview,
        )
    except PDFParseError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    doc = DOCUMENT_STORE.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "filename": doc.filename, "pages": doc.pages}

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest, agent: AgnoAgent = Depends(get_agent)):
    async def token_generator() -> AsyncGenerator[bytes, None]:
        try:
            async for token in agent.stream_answer(req.session_id, req.query):
                if token.startswith("__STEP__"):
                    step = token.replace("__STEP__", "").strip("_")
                    payload = {"token": "", "done": False, "step": step}
                    yield (f"{payload}\n").encode("utf-8")
                    continue
                if token == "__DONE__":
                    payload = {"token": "", "done": True}
                    yield (f"{payload}\n").encode("utf-8")
                    break
                payload = {"token": token, "done": False}
                yield (f"{payload}\n").encode("utf-8")
                await asyncio.sleep(0)
        except Exception as e:
            payload = {"token": f"[ERROR] {e}", "done": True}
            yield (f"{payload}\n").encode("utf-8")

    return StreamingResponse(token_generator(), media_type="text/plain")

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API — up. See /docs for API UI."}
