"""
Activity log data model for tracking all system activities.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ActivityLog(Base):
    """Model for tracking all system activities"""
    __tablename__ = "activity_logs"
    
    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Request information
    endpoint = Column(String(256), nullable=False)
    method = Column(String(16), nullable=False)
    path = Column(String(256), nullable=False)
    ip_address = Column(String(45), nullable=True)
    
    # User information (if authentication is implemented)
    user_id = Column(String(64), nullable=True, index=True)
    
    # Request details
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Performance metrics
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    
    # Status information
    status_code = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=True)
    
    # Error information (if any)
    error = Column(Text, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, endpoint={self.endpoint}, method={self.method}, status={self.status_code})>" 