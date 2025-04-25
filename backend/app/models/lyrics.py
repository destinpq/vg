"""
Lyrics data models.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Lyrics(Base):
    """Lyrics model for tracking generated lyrics prompts"""
    __tablename__ = "lyrics"
    
    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Lyrics information
    original_text = Column(Text, nullable=False)
    language = Column(String(32), default="english")
    status = Column(String(32), default="pending")  # pending, processing, completed, failed
    
    # Style information
    style = Column(String(64), nullable=True)
    
    # Results
    prompts = Column(JSON, nullable=True)  # Array of generated prompts
    
    # Error information (if any)
    error = Column(Text, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Lyrics(id={self.id}, status={self.status})>" 