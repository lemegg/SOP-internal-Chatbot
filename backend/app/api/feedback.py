from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, QueryLog, QueryFeedback
from pydantic import BaseModel, field_validator

router = APIRouter()

class FeedbackRequest(BaseModel):
    query_log_id: int
    feedback: str

    @field_validator('feedback')
    @classmethod
    def validate_feedback(cls, v: str) -> str:
        if v not in ('like', 'dislike'):
            raise ValueError('feedback must be "like" or "dislike"')
        return v

@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if query_log exists
    query_log = db.query(QueryLog).filter(QueryLog.id == request.query_log_id).first()
    if not query_log:
        raise HTTPException(status_code=404, detail="Query log not found")

    # Check for duplicate feedback
    existing_feedback = db.query(QueryFeedback).filter(
        QueryFeedback.query_log_id == request.query_log_id,
        QueryFeedback.user_id == current_user.id
    ).first()
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this query")

    # Create feedback
    new_feedback = QueryFeedback(
        query_log_id=request.query_log_id,
        user_id=current_user.id,
        feedback_type=request.feedback
    )
    db.add(new_feedback)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": "Feedback recorded"}
