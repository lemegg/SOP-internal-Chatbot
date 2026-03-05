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
    if current_user.email.lower() not in settings.allowed_emails:
        raise HTTPException(status_code=403, detail="Not authorized to access analytics")
    
    days = 7 if range == "weekly" else 30
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 1. Get top queries first
    top_results = (
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
    
    final_results = []
    for rank, (query_text, count) in enumerate(top_results, 1):
        # 2. For each query, calculate feedback stats
        # Get all log IDs for this specific query text
        log_ids = db.query(QueryLog.id).filter(QueryLog.query_text == query_text).all()
        log_id_list = [l[0] for l in log_ids]
        
        # Count likes and dislikes
        likes = db.query(func.count(QueryFeedback.id)).filter(
            QueryFeedback.query_log_id.in_(log_id_list),
            QueryFeedback.feedback_type == "like"
        ).scalar()
        
        dislikes = db.query(func.count(QueryFeedback.id)).filter(
            QueryFeedback.query_log_id.in_(log_id_list),
            QueryFeedback.feedback_type == "dislike"
        ).scalar()
        
        total_feedback = likes + dislikes
        pos_pct = 0
        neg_pct = 0
        
        if total_feedback > 0:
            pos_pct = round((likes / total_feedback) * 100)
            neg_pct = round((dislikes / total_feedback) * 100)
            
        final_results.append({
            "rank": rank,
            "query": query_text,
            "count": count,
            "positive_percent": pos_pct if total_feedback > 0 else None,
            "negative_percent": neg_pct if total_feedback > 0 else None,
            "total_feedback": total_feedback
        })
    
    return {
        "range": range,
        "top_queries": final_results
    }

@router.get("/query-log/monthly")
def get_monthly_query_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email.lower() not in settings.allowed_emails:
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

@router.get("/sop-missed")
def get_sop_missed_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email.lower() not in settings.allowed_emails:
        raise HTTPException(status_code=403, detail="Not authorized to access analytics")
    
    results = (
        db.query(
            QueryLog.query_text,
            QueryLog.timestamp,
            User.email
        )
        .join(User, QueryLog.user_id == User.id)
        .filter(QueryLog.response_status == "not_found")
        .order_by(QueryLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    logs = []
    for r in results:
        logs.append({
            "query": r[0],
            "timestamp": r[1].isoformat(),
            "person": r[2]
        })
        
    return {"logs": logs}
