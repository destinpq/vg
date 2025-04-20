"""
Middleware module for the application.
"""
from .error_handlers import register_error_handlers
from .request_logger import RequestLoggerMiddleware

__all__ = ["register_error_handlers", "RequestLoggerMiddleware"] 