"""
Controller for activity logs.
"""
import logging
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional
from datetime import datetime

from ..services.log_service import log_service
from ..schemas.activity_log import ActivityLogResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/", response_model=dict)
async def get_logs(
    limit: int = Query(100, description="Maximum number of logs to return"),
    offset: int = Query(0, description="Offset for pagination"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    # In a real app, we'd also add date range filters
):
    """
    Get activity logs with optional filtering and pagination.
    """
    try:
        result = await log_service.get_logs(
            limit=limit,
            offset=offset,
            endpoint=endpoint,
            method=method,
            status_code=status_code
        )
        
        return {
            "logs": result["logs"],
            "total": result["total"],
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < result["total"]
        }
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@router.get("/{log_id}", response_model=ActivityLogResponse)
async def get_log(
    log_id: str = Path(..., description="ID of the log to retrieve")
):
    """
    Get a specific activity log by ID.
    """
    try:
        from ..models.activity_log import ActivityLog
        log = await log_service.db.get(ActivityLog, log_id)
        
        if not log:
            raise HTTPException(status_code=404, detail=f"Log with ID {log_id} not found")
            
        return log
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving log: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving log: {str(e)}")

@router.get("/stats/overview", response_model=dict)
async def get_log_stats():
    """
    Get overview statistics about the logs.
    """
    try:
        from ..models.activity_log import ActivityLog
        from sqlalchemy import func, select
        
        # For a simple implementation, we'll just return the total count
        # In a real app, we'd add more meaningful statistics
        count = await log_service.db.count(ActivityLog)
        
        # Count by status code
        # This would be a more complex query in a real app
        # We'd use more sophisticated SQL with group by
        
        return {
            "total_logs": count,
            "stats": {
                "success_rate": 0,  # Placeholder
                "average_duration_ms": 0,  # Placeholder
                "requests_per_minute": 0,  # Placeholder
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving log stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving log stats: {str(e)}")

@router.delete("/{log_id}", response_model=dict)
async def delete_log(
    log_id: str = Path(..., description="ID of the log to delete")
):
    """
    Delete a specific activity log by ID.
    """
    try:
        from ..models.activity_log import ActivityLog
        deleted = await log_service.db.delete(ActivityLog, log_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Log with ID {log_id} not found")
            
        return {"success": True, "message": f"Log {log_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting log: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting log: {str(e)}") 