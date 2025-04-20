"""
Backend application entry point.
"""
import uvicorn

if __name__ == "__main__":
    """Start the application server"""
    uvicorn.run("app.app:app", host="0.0.0.0", port=5001, reload=True)
