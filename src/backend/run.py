"""
Development server entry point.
Run this file to start the FastAPI server locally.
"""
import uvicorn
from .config import settings


if __name__ == "__main__":
    print("=" * 60)
    print("Vila Acadia - Timesheet API Server")
    print("=" * 60)
    print(f"Starting server on {settings.host}:{settings.port}")
    print(f"Google Sheet ID: {settings.google_sheet_id}")
    print(f"API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"Health Check: http://{settings.host}:{settings.port}/health")
    print("=" * 60)
    
    uvicorn.run(
        "src.backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )


