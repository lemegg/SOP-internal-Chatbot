from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    retrieved_sop = Column(Text)
    response_status = Column(String)
    user = relationship("User")

class QueryFeedback(Base):
    __tablename__ = "query_feedback"
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, ForeignKey("query_logs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    feedback_type = Column(String) # "like" or "dislike"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('query_log_id', 'user_id', name='_user_query_feedback_uc'),)
    
    query_log = relationship("QueryLog")
    user = relationship("User")
