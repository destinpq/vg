"""
Database service for accessing the database.
"""
import logging
from typing import TypeVar, Type, Optional, List, Any, Dict, Generic
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update, delete, func

from ..models.base import Base
from ..config.settings import settings

# Type variable for Model classes
T = TypeVar('T')

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for accessing the database."""
    
    def __init__(self):
        """Initialize the database service with async engine."""
        # Create async engine
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True
        )
        
        # Create session factory
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        logger.info(f"Database service initialized with URL: {settings.DATABASE_URL}")
    
    async def create_tables(self):
        """Create all tables defined in the models."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    
    async def get_session(self) -> AsyncSession:
        """Get a new session for database operations."""
        return self.async_session()
    
    async def add(self, obj: T) -> T:
        """Add an object to the database."""
        async with self.async_session() as session:
            session.add(obj)
            await session.commit()
            return obj
    
    async def commit(self):
        """Commit the current session."""
        async with self.async_session() as session:
            await session.commit()
    
    async def get(self, model: Type[T], id: Any) -> Optional[T]:
        """Get an object by its ID."""
        async with self.async_session() as session:
            result = await session.execute(select(model).filter(model.id == id))
            return result.scalar_one_or_none()
    
    async def list(
        self, 
        model: Type[T], 
        limit: int = None, 
        offset: int = None, 
        order_by: str = None, 
        order_dir: str = "asc",
        **filters
    ) -> List[T]:
        """List objects with optional filters, pagination and ordering."""
        async with self.async_session() as session:
            query = select(model)
            
            # Apply filters if any
            for attr, value in filters.items():
                if hasattr(model, attr):
                    query = query.filter(getattr(model, attr) == value)
            
            # Apply ordering if specified
            if order_by and hasattr(model, order_by):
                if order_dir.lower() == "desc":
                    query = query.order_by(getattr(model, order_by).desc())
                else:
                    query = query.order_by(getattr(model, order_by))
            
            # Apply pagination if specified
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def count(self, model: Type[T], **filters) -> int:
        """Count objects with optional filters."""
        async with self.async_session() as session:
            query = select(func.count(model.id))
            
            # Apply filters if any
            for attr, value in filters.items():
                if hasattr(model, attr):
                    query = query.filter(getattr(model, attr) == value)
            
            result = await session.execute(query)
            return result.scalar_one()
    
    async def update(self, model: Type[T], id: Any, **values) -> bool:
        """Update an object by its ID with the given values."""
        async with self.async_session() as session:
            query = update(model).where(model.id == id).values(**values)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0
    
    async def delete(self, model: Type[T], id: Any) -> bool:
        """Delete an object by its ID."""
        async with self.async_session() as session:
            query = delete(model).where(model.id == id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

# Create a singleton instance
db_service = DatabaseService() 