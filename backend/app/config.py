"""
This module forwards to app.utils.config for backward compatibility.
"""

from app.utils.config import Settings, get_settings, verify_settings

# Create a settings instance for direct import
settings = get_settings() 