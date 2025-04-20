"""
Video data models.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Video(Base):
    """Video model for tracking generated videos"""
    __tablename__ = "videos"
    
    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Video information
    prompt = Column(Text, nullable=False)
    status = Column(String(32), default="pending")  # pending, processing, completed, failed
    
    # Video file information
    file_path = Column(String(256), nullable=True)
    web_path = Column(String(256), nullable=True)
    duration = Column(Float, nullable=True)
    
    # Generation parameters
    width = Column(Integer, default=512)
    height = Column(Integer, default=512)
    fps = Column(Integer, default=24)
    num_inference_steps = Column(Integer, default=50)
    
    # Generation metrics
    processing_time = Column(Float, nullable=True)
    
    # Error information (if any)
    error = Column(Text, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Video(id={self.id}, status={self.status}, prompt='{self.prompt[:30]}...')>" 