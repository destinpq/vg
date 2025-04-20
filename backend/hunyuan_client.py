#!/usr/bin/env python3
"""
Hunyuan Client for backwards compatibility.
This module forwards to app.clients.hunyuan_client for MVC structure.
"""
from app.clients.hunyuan_client import hunyuan_client, HunyuanClient

# Expose the same functions and classes for backward compatibility
__all__ = ["hunyuan_client", "HunyuanClient"]

# For direct import
if __name__ == "__main__":
    # Testing code
    import json
    
    client = HunyuanClient()
    
    # Check health
    health = client.check_health()
    print("Health check result:", json.dumps(health, indent=2))
    
    if health.get("status") == "healthy":
        # Generate a test video
        prompt = "A cat playing piano, cinematic quality, 4K"
        result = client.generate_video(prompt)
        print("Generation result:", json.dumps(result, indent=2)) 