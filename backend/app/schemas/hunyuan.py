"""
Hunyuan schema models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class HunyuanGenerationRequest(BaseModel):
    """Request model for Hunyuan video generation."""
    prompt: str = Field(..., description="Text prompt describing the video to generate")
    num_inference_steps: int = Field(50, description="Number of inference steps")
    height: int = Field(320, description="Video height in pixels")
    width: int = Field(576, description="Video width in pixels")
    output_format: str = Field("gif", description="Output format (gif or mp4)")

class HunyuanGenerationResponse(BaseModel):
    """Response model for Hunyuan video generation request."""
    status: str = Field(..., description="Status of the generation (pending, success, error)")
    request_id: str = Field(..., description="Unique ID for the generation request")
    task_id: str = Field(..., description="Task ID in the processing queue")
    message: str = Field(..., description="Status message")
    prompt: str = Field(..., description="Original prompt")
    parameters: Dict[str, Any] = Field(..., description="Generation parameters")

class HunyuanStatusResponse(BaseModel):
    """Response model for Hunyuan API status check."""
    status: str = Field(..., description="Status of the API (ok or error)")
    hunyuan_api: Dict[str, Any] = Field(..., description="Hunyuan API health status")
    server_time: str = Field(..., description="Server time") 