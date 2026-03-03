from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from app.core.auth import get_current_user
from app.models.models import User, QueryLog
from app.core.database import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()
retriever = Retriever()
generator = Generator()

class Answer(BaseModel):
    summary: str
    steps: List[str]
    rules: List[str]
    notes: List[str]

class Source(BaseModel):
    sop: str
    section: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: Answer
    sources: List[Source]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Retrieve chunks
        context_chunks = retriever.retrieve(request.query)
        
        # Generate structured answer
        result = generator.generate_answer(request.query, context_chunks)
        
        # Log the query
        sop_names = list(set([c.get("sop_name", c.get("sop", "Unknown")) for c in context_chunks]))
        log = QueryLog(
            user_id=current_user.id,
            query_text=request.query,
            retrieved_sop=", ".join(sop_names),
            response_status="SUCCESS"
        )
        db.add(log)
        db.commit()
        
        return ChatResponse(**result)
    except Exception as e:
        # Log failure
        log = QueryLog(
            user_id=current_user.id,
            query_text=request.query,
            response_status=f"FAILED: {str(e)}"
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
