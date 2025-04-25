from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models
from ..api import schemas
import uuid
from typing import List, Optional
from datetime import datetime

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    # In a real app you'd hash the password here
    hashed_password = user.password  # Placeholder for password hashing
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

# Video CRUD operations
def create_video(
    db: Session, 
    video: schemas.VideoBase, 
    model_type: str, 
    creator_id: Optional[int] = None
) -> models.Video:
    """Create a new video entry"""
    
    # Generate a unique video ID
    video_id = f"{model_type.lower()}_{uuid.uuid4().hex[:8]}"
    
    db_video = models.Video(
        video_id=video_id,
        title=video.title,
        description=video.description,
        prompt=video.prompt,
        status="queued",
        model_type=model_type,
        creator_id=creator_id
    )
    
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_video(db: Session, video_id: str) -> Optional[models.Video]:
    """Get video by ID"""
    return db.query(models.Video).filter(models.Video.video_id == video_id).first()

def get_videos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    creator_id: Optional[int] = None
) -> List[models.Video]:
    """Get list of videos with optional filtering by creator"""
    query = db.query(models.Video)
    
    if creator_id is not None:
        query = query.filter(models.Video.creator_id == creator_id)
        
    return query.order_by(models.Video.created_at.desc()).offset(skip).limit(limit).all()

def update_video_status(
    db: Session, 
    video_id: str, 
    status: str, 
    file_path: Optional[str] = None,
    thumbnail_path: Optional[str] = None
) -> Optional[models.Video]:
    """Update video status and paths"""
    db_video = get_video(db, video_id)
    
    if not db_video:
        return None
    
    db_video.status = status
    
    if file_path:
        db_video.file_path = file_path
        
    if thumbnail_path:
        db_video.thumbnail_path = thumbnail_path
    
    db_video.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video_metadata(
    db: Session,
    video_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    duration: Optional[float] = None,
    fps: Optional[int] = None,
    parameters: Optional[dict] = None
) -> Optional[models.Video]:
    """Update video metadata"""
    db_video = get_video(db, video_id)
    
    if not db_video:
        return None
    
    if width is not None:
        db_video.width = width
        
    if height is not None:
        db_video.height = height
        
    if duration is not None:
        db_video.duration = duration
        
    if fps is not None:
        db_video.fps = fps
        
    if parameters is not None:
        db_video.parameters = parameters
    
    db_video.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_video)
    return db_video

# Lyrics CRUD operations
def create_lyric_prompt(
    db: Session, 
    video_id: str, 
    lyrics: str, 
    prompts: List[dict],
    model_used: Optional[str] = None
) -> models.LyricPrompt:
    """Create a new lyric prompt entry"""
    db_lyric = models.LyricPrompt(
        video_id=video_id,
        lyrics=lyrics,
        prompts=prompts,
        model_used=model_used
    )
    
    db.add(db_lyric)
    db.commit()
    db.refresh(db_lyric)
    return db_lyric

def get_lyric_prompt(db: Session, video_id: str) -> Optional[models.LyricPrompt]:
    """Get lyric prompt by video ID"""
    return db.query(models.LyricPrompt).filter(models.LyricPrompt.video_id == video_id).first()

# Audio analysis CRUD operations
def create_audio_analysis(
    db: Session,
    video_id: str,
    beats: List[float],
    tempo: float,
    segments: List[dict]
) -> models.AudioAnalysis:
    """Create a new audio analysis entry"""
    db_analysis = models.AudioAnalysis(
        video_id=video_id,
        beats=beats,
        tempo=tempo,
        segments=segments
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def get_audio_analysis(db: Session, video_id: str) -> Optional[models.AudioAnalysis]:
    """Get audio analysis by video ID"""
    return db.query(models.AudioAnalysis).filter(models.AudioAnalysis.video_id == video_id).first() 