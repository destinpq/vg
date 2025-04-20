"""
Request logging middleware.
This middleware logs all requests and responses to the database.
"""
import json
import time
import logging
from typing import Callable, Dict, Any
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..services.log_service import log_service

# Configure logging
logger = logging.getLogger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses to the database."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request, log it, and pass it to the next middleware."""
        # Start timing the request
        start_time = datetime.utcnow()
        
        # Extract request information
        method = request.method
        path = request.url.path
        endpoint = self._get_endpoint_name(path)
        ip_address = self._get_client_ip(request)
        
        # Get request body if it's available
        request_body = await self._get_request_body(request)
        
        # Log request to database
        log_entry = await log_service.log_request(
            endpoint=endpoint,
            method=method,
            path=path,
            ip_address=ip_address,
            request_data=request_body
        )
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Extract response information
            status_code = response.status_code
            response_body = await self._get_response_body(response)
            
            # Log response to database
            await log_service.log_response(
                log_entry=log_entry,
                status_code=status_code,
                response_data=response_body
            )
            
            return response
        except Exception as e:
            # Log the error
            if log_entry:
                await log_service.log_response(
                    log_entry=log_entry,
                    status_code=500,
                    error=str(e)
                )
            # Re-raise the exception
            raise
    
    def _get_endpoint_name(self, path: str) -> str:
        """Extract endpoint name from path."""
        # Remove query parameters if any
        path = path.split("?")[0]
        
        # Split path into parts
        parts = [p for p in path.split("/") if p]
        
        if not parts:
            return "/"
        
        # Try to determine the controller/action
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        
        return f"{parts[0]}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check forwarded header first (for clients behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Otherwise use the client's direct IP
        return request.client.host if request.client else None
    
    async def _get_request_body(self, request: Request) -> Dict[str, Any]:
        """Get request body as a dictionary."""
        try:
            # Try to read the body, but this can only be done once
            # so we need to set the body back afterwards
            body = await request.body()
            
            # Set the body back for downstream processing
            # This is necessary because once read, the body is consumed
            async def receive():
                return {"type": "http.request", "body": body}
            
            request._receive = receive
            
            # Try to parse as JSON
            if body:
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    # Not JSON, just return a simple message
                    return {"body_type": "raw", "size": len(body)}
            
            return {}
        except Exception as e:
            logger.error(f"Error reading request body: {e}")
            return {"error": "Could not read request body"}
    
    async def _get_response_body(self, response: Response) -> Dict[str, Any]:
        """Get response body as a dictionary."""
        try:
            # Access the response body if available
            body = getattr(response, "body", None)
            
            if body:
                try:
                    # Try to parse as JSON
                    return json.loads(body)
                except json.JSONDecodeError:
                    # Not JSON, just return a simple message
                    return {"body_type": "raw", "size": len(body)}
            
            return {}
        except Exception as e:
            logger.error(f"Error reading response body: {e}")
            return {"error": "Could not read response body"} 