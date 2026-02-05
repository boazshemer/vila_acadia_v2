"""
FastAPI application for Vila Acadia timesheet system.
Provides authentication and Google Sheets integration.
"""
import logging
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from .models import (
    AuthRequest, AuthResponse, HealthResponse,
    HoursSubmissionRequest, HoursSubmissionResponse,
    DailyTipRequest, DailyTipResponse,
    ManagerAuthRequest, ManagerAuthResponse
)
from .gsheets_service import gs_service
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes Google Sheets connection on startup.
    """
    # Startup: Initialize Google Sheets connection
    try:
        gs_service.connect()
        logger.info("✓ Connected to Google Sheets successfully")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Google Sheets: {e}", exc_info=True)
        logger.warning("Application will continue, but API calls may fail")
    
    yield
    
    # Shutdown: cleanup if needed
    logger.info("Shutting down application...")


# Initialize FastAPI app
app = FastAPI(
    title="Vila Acadia Timesheet API",
    description="Backend API for employee timesheet management using Google Sheets",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),  # Whitelist specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Determine static files path
STATIC_DIR = Path(__file__).parent.parent.parent / "static"
if not STATIC_DIR.exists():
    logger.warning(f"Static directory not found at {STATIC_DIR}. Frontend will not be served.")
    STATIC_DIR = None


@app.get("/api", tags=["Root"])
async def root():
    """API root endpoint - API information."""
    return {
        "service": "Vila Acadia Timesheet API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/verify",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Verifies connectivity to Google Sheets.
    """
    try:
        result = gs_service.health_check()
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"]
            )
        
        return HealthResponse(
            status=result["status"],
            spreadsheet_id=result["spreadsheet_id"],
            spreadsheet_title=result.get("spreadsheet_title", ""),
            message=result["message"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.post("/auth/verify", response_model=AuthResponse, tags=["Authentication"])
async def verify_auth(auth_request: AuthRequest):
    """
    Verify employee authentication using PIN.
    
    This endpoint checks the provided name and PIN against
    the Settings sheet in Google Sheets.
    
    Args:
        auth_request: Contains employee name and 4-digit PIN
    
    Returns:
        AuthResponse with success status and message
    """
    try:
        # Verify credentials against Google Sheets
        is_valid = gs_service.verify_employee_pin(
            name=auth_request.name,
            pin=auth_request.pin
        )
        
        if is_valid:
            return AuthResponse(
                success=True,
                message="Authentication successful",
                employee_name=auth_request.name
            )
        else:
            return AuthResponse(
                success=False,
                message="Invalid credentials. Please check your name and PIN.",
                employee_name=""
            )
    
    except Exception as e:
        # Log error for debugging but don't expose details to client
        logger.error(f"Authentication error for user {auth_request.name}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )


@app.post("/manager/auth", response_model=ManagerAuthResponse, tags=["Manager"])
async def manager_auth(request: ManagerAuthRequest):
    """
    Authenticate manager with password.
    
    This endpoint verifies the manager password against the configured value.
    In a production system, this should use proper JWT tokens and hashed passwords.
    
    Args:
        request: Contains manager password
    
    Returns:
        ManagerAuthResponse with success status and token
    """
    try:
        # Simple password check (in production, use hashed passwords + JWT)
        if request.password == settings.manager_password:
            # In production, generate a proper JWT token here
            token = "manager_authenticated"  # Placeholder - use JWT in production
            logger.info("Manager authenticated successfully")
            return ManagerAuthResponse(
                success=True,
                message="Authentication successful",
                token=token
            )
        else:
            logger.warning("Failed manager authentication attempt")
            return ManagerAuthResponse(
                success=False,
                message="Invalid password",
                token=None
            )
    
    except Exception as e:
        logger.error(f"Manager authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )


@app.post("/submit-hours", response_model=HoursSubmissionResponse, tags=["Time Entry"])
async def submit_hours(request: HoursSubmissionRequest):
    """
    Submit hours worked for an employee.
    
    This endpoint:
    1. Verifies the employee exists in Settings
    2. Checks if the month is still open (before 2nd of next month)
    3. Calculates hours from start/end time
    4. Creates date column if needed
    5. Checks cell is empty (no overwrite)
    6. Writes hours to the appropriate cell
    
    Args:
        request: Contains employee name, date, start time, and end time
    
    Returns:
        HoursSubmissionResponse with success status and calculated hours
    """
    try:
        # Check if month is closed
        if gs_service.is_month_closed(request.date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Month is closed for submissions. Cutoff date has passed."
            )
        
        # Verify employee exists in Settings
        employees = gs_service.get_employee_settings()
        employee_exists = any(
            emp["name"].lower() == request.employee_name.lower() 
            for emp in employees
        )
        
        if not employee_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee '{request.employee_name}' not found in Settings"
            )
        
        # Calculate hours
        hours = gs_service.calculate_hours(request.start_time, request.end_time)
        
        # Submit hours to sheet
        result = gs_service.submit_hours(
            employee_name=request.employee_name,
            date=request.date,
            hours=hours
        )
        
        return HoursSubmissionResponse(
            success=True,
            message=f"Hours submitted successfully to {result['worksheet']}!",
            hours_worked=hours,
            date=request.date
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hours submission error for {request.employee_name} on {request.date}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit hours: {str(e)}"
        )


@app.post("/manager/submit-daily-tip", response_model=DailyTipResponse, tags=["Manager"])
async def submit_daily_tip(request: DailyTipRequest):
    """
    Submit total daily tips and trigger formula calculations.
    
    This endpoint (manager only):
    1. Checks if month is still open
    2. Creates date column if needed
    3. Writes total tips (T) to Totals section
    4. Injects formulas for:
       - Total Hours (H) = SUM of all employee hours
       - Tip Rate (R) = T / H
       - Individual Payouts (Pi) = hi × R
    
    Args:
        request: Contains date and total tips amount
    
    Returns:
        DailyTipResponse with success status and formula injection confirmation
    """
    try:
        # Check if month is closed
        if gs_service.is_month_closed(request.date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Month is closed for submissions. Cutoff date has passed."
            )
        
        # Submit tips and inject formulas
        result = gs_service.submit_daily_tips(
            date=request.date,
            total_tips=request.total_tips
        )
        
        return DailyTipResponse(
            success=True,
            message=f"Daily tips submitted successfully. Formulas calculated for {result['employee_count']} employees.",
            date=request.date,
            total_tips=request.total_tips,
            formulas_injected=result["formulas_injected"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily tip submission error for {request.date}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit daily tips: {str(e)}"
        )


# Mount static files and serve frontend (must be after all API routes)
if STATIC_DIR and STATIC_DIR.exists():
    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """
        Catch-all route to serve frontend index.html for client-side routing.
        This must be defined after all API routes to avoid conflicts.
        """
        # Check if file exists in static directory
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise serve index.html for client-side routing
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        raise HTTPException(status_code=404, detail="Not found")


# Development server runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

