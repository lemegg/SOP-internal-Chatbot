from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, QueryLog
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
