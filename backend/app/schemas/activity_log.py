"""
Activity log schema models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ActivityLogCreate(BaseModel):
    """Schema for creating an activity log entry."""
    endpoint: str = Field(..., description="API endpoint that was called")
    method: str = Field(..., description="HTTP method used")
    path: str = Field(..., description="Full request path")
    ip_address: Optional[str] = Field(None, description="IP address of the client")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request data/body")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data/body")
    start_time: datetime = Field(..., description="Request start time")
    end_time: Optional[datetime] = Field(None, description="Request end time")
    duration_ms: Optional[float] = Field(None, description="Request duration in milliseconds")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    success: Optional[bool] = Field(None, description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ActivityLogResponse(BaseModel):
    """Schema for activity log response."""
    id: str = Field(..., description="Unique identifier for the log entry")
    created_at: datetime = Field(..., description="When the log entry was created")
    endpoint: str = Field(..., description="API endpoint that was called")
    method: str = Field(..., description="HTTP method used")
    path: str = Field(..., description="Full request path")
    ip_address: Optional[str] = Field(None, description="IP address of the client")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request data/body")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data/body")
    start_time: datetime = Field(..., description="Request start time")
    end_time: Optional[datetime] = Field(None, description="Request end time")
    duration_ms: Optional[float] = Field(None, description="Request duration in milliseconds")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    success: Optional[bool] = Field(None, description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        orm_mode = True 