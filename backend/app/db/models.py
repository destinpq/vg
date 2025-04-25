from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    videos = relationship("Video", back_populates="creator")

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)  # External ID for the video
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    prompt = Column(Text)
    status = Column(String)  # queued, processing, completed, failed
    model_type = Column(String)  # hunyuan, mochi, etc.
    file_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    fps = Column(Integer, nullable=True)
    parameters = Column(JSON, nullable=True)  # Store generation parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="videos")
    
class LyricPrompt(Base):
    __tablename__ = "lyric_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)  # Reference to the video
    lyrics = Column(Text)
    prompts = Column(JSON)  # JSON array of generated prompts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_used = Column(String, nullable=True)  # Which model generated the prompts
    
class AudioAnalysis(Base):
    __tablename__ = "audio_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)  # Reference to the video
    beats = Column(JSON, nullable=True)  # Beat timestamps
    tempo = Column(Float, nullable=True)  # Tempo in BPM
    segments = Column(JSON, nullable=True)  # Audio segments
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 