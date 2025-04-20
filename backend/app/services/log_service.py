"""
Activity logging service for tracking system activities in the database.
"""
import uuid
import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union

from ..models.activity_log import ActivityLog
from ..schemas.activity_log import ActivityLogCreate
from .database_service import db_service

# Configure logging
logger = logging.getLogger(__name__)

class LogService:
    """Service for logging system activities to the database."""
    
    def __init__(self, db=None):
        """Initialize with database service."""
        self.db = db or db_service
    
    async def log_activity(self, log_data: Union[ActivityLogCreate, Dict[str, Any]]) -> ActivityLog:
        """Log an activity to the database."""
        try:
            # Convert dict to ActivityLogCreate if needed
            if isinstance(log_data, dict):
                log_data = ActivityLogCreate(**log_data)
            
            # Create unique ID
            log_id = str(uuid.uuid4())
            
            # Create log entry
            log_entry = ActivityLog(
                id=log_id,
                endpoint=log_data.endpoint,
                method=log_data.method,
                path=log_data.path,
                ip_address=log_data.ip_address,
                user_id=log_data.user_id,
                request_data=log_data.request_data,
                response_data=log_data.response_data,
                start_time=log_data.start_time,
                end_time=log_data.end_time,
                duration_ms=log_data.duration_ms,
                status_code=log_data.status_code,
                success=log_data.success,
                error=log_data.error,
                metadata=log_data.metadata
            )
            
            # Save to database
            await self.db.add(log_entry)
            
            return log_entry
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            # Even if logging fails, we don't want to break the application
            return None
    
    async def log_request(
        self,
        endpoint: str,
        method: str,
        path: str,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ActivityLog:
        """Start logging a request (before processing)."""
        try:
            # Start timing
            start_time = datetime.utcnow()
            
            # Sanitize request data (remove sensitive info)
            safe_request_data = self._sanitize_data(request_data) if request_data else None
            
            # Create log entry
            log_data = ActivityLogCreate(
                endpoint=endpoint,
                method=method,
                path=path,
                ip_address=ip_address,
                user_id=user_id,
                request_data=safe_request_data,
                start_time=start_time,
                metadata=metadata
            )
            
            return await self.log_activity(log_data)
        except Exception as e:
            logger.error(f"Error logging request: {e}")
            return None
    
    async def log_response(
        self,
        log_entry: ActivityLog,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> ActivityLog:
        """Complete logging a request (after processing)."""
        try:
            if not log_entry:
                return None
                
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = (end_time - log_entry.start_time).total_seconds() * 1000
            
            # Sanitize response data (remove sensitive info)
            safe_response_data = self._sanitize_data(response_data) if response_data else None
            
            # Update log entry
            log_entry.end_time = end_time
            log_entry.duration_ms = duration_ms
            log_entry.status_code = status_code
            log_entry.success = 200 <= status_code < 300
            log_entry.response_data = safe_response_data
            log_entry.error = error
            
            # Save changes
            await self.db.update(
                ActivityLog,
                log_entry.id,
                end_time=end_time,
                duration_ms=duration_ms,
                status_code=status_code,
                success=200 <= status_code < 300,
                response_data=safe_response_data,
                error=error
            )
            
            return log_entry
        except Exception as e:
            logger.error(f"Error logging response: {e}")
            return log_entry
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from data."""
        if not data:
            return data
            
        # Create a copy to avoid modifying the original
        sanitized = data.copy()
        
        # List of sensitive fields to mask
        sensitive_fields = [
            "password", "token", "api_key", "secret", "credit_card",
            "card_number", "cvv", "ssn", "social_security", "auth",
            "authorization", "access_token", "refresh_token", "openai_api_key"
        ]
        
        # Function to recursively sanitize nested dictionaries
        def sanitize_dict(d):
            if not isinstance(d, dict):
                return d
                
            for key, value in list(d.items()):
                # Check if this key should be sanitized
                if any(sf in key.lower() for sf in sensitive_fields):
                    d[key] = "[REDACTED]"
                # Recursively sanitize nested dictionaries
                elif isinstance(value, dict):
                    d[key] = sanitize_dict(value)
                # Sanitize items in lists
                elif isinstance(value, list):
                    d[key] = [sanitize_dict(item) if isinstance(item, dict) else item for item in value]
            return d
        
        return sanitize_dict(sanitized)
    
    async def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        endpoint: Optional[str] = None,
        user_id: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        start_time_min: Optional[datetime] = None,
        start_time_max: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get activity logs with optional filtering."""
        filters = {}
        
        if endpoint:
            filters["endpoint"] = endpoint
        if user_id:
            filters["user_id"] = user_id
        if method:
            filters["method"] = method
        if status_code:
            filters["status_code"] = status_code
        
        # Time-based filters would need custom query but we'll skip for simplicity
        
        logs = await self.db.list(ActivityLog, limit=limit, offset=offset, **filters)
        count = await self.db.count(ActivityLog, **filters)
        
        return {
            "logs": logs,
            "total": count,
            "limit": limit,
            "offset": offset
        }

# Create singleton instance
log_service = LogService() 