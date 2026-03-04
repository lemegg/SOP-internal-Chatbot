from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, QueryLog, QueryFeedback
from app.core.config import settings
from typing import List

router = APIRouter()

@router.get("/top-queries")
def get_top_queries(
    range: str = Query("weekly", regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email not in settings.allowed_emails:
        raise HTTPException(status_code=403, detail="Not authorized to access analytics")
    
    days = 7 if range == "weekly" else 30
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = (
        db.query(
            QueryLog.query_text,
            func.count(QueryLog.id).label("count")
        )
        .filter(QueryLog.timestamp >= start_date)
        .group_by(QueryLog.query_text)
        .order_by(func.count(QueryLog.id).desc())
        .limit(15)
        .all()
    )
    
    return {
        "range": range,
        "top_queries": [{"query": r[0], "count": r[1]} for r in results]
    }

@router.get("/query-log/monthly")
def get_monthly_query_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email not in settings.allowed_emails:
        raise HTTPException(status_code=403, detail="Not authorized to access analytics")
    
    start_date = datetime.utcnow() - timedelta(days=30)
    
    # Query with joins to User and QueryFeedback
    # We use a subquery or conditional logic for feedback prioritization if multiple exist
    # But since the unique constraint prevents multiple feedback per user/query, 
    # we just need to join.
    results = (
        db.query(
            QueryLog.query_text,
            QueryLog.timestamp,
            User.email,
            QueryFeedback.feedback_type
        )
        .join(User, QueryLog.user_id == User.id)
        .outerjoin(QueryFeedback, QueryLog.id == QueryFeedback.query_log_id)
        .filter(QueryLog.timestamp >= start_date)
        .order_by(QueryLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    logs = []
    for r in results:
        logs.append({
            "query": r[0],
            "timestamp": r[1].isoformat(),
            "person": r[2],
            "feedback": r[3]
        })
        
    return {"logs": logs}
