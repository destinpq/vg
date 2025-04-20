"""
Error handling middleware.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers for the application"""
    
    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc: StarletteHTTPException):
        """Custom 404 handler for file not found errors"""
        if request.url.path.startswith("/output/"):
            return JSONResponse(
                status_code=404,
                content={
                    "error": "File not found",
                    "message": "The requested video file is not available. It may still be processing or does not exist."
                }
            )
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"URL {request.url.path} not found",
                "documentation": "/docs"
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Generic HTTP exception handler"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for uncaught exceptions"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc) if str(exc) else "An unexpected error occurred"
            }
        ) 