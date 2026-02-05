"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, time
from typing import Optional


class AuthRequest(BaseModel):
    """Request model for PIN authentication."""
    name: str = Field(..., min_length=1, description="Employee name")
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN")
    
    @field_validator("pin")
    @classmethod
    def validate_pin_digits(cls, v: str) -> str:
        """Ensure PIN contains only digits."""
        if not v.isdigit():
            raise ValueError("PIN must contain only digits")
        return v


class AuthResponse(BaseModel):
    """Response model for authentication."""
    success: bool = Field(..., description="Whether authentication succeeded")
    message: str = Field(..., description="Status message")
    employee_name: str = Field(default="", description="Authenticated employee name")


class ManagerAuthRequest(BaseModel):
    """Request model for manager authentication."""
    password: str = Field(..., min_length=1, description="Manager password")


class ManagerAuthResponse(BaseModel):
    """Response model for manager authentication."""
    success: bool = Field(..., description="Whether authentication succeeded")
    message: str = Field(..., description="Status message")
    token: Optional[str] = Field(default=None, description="Authentication token (if successful)")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    spreadsheet_id: str = Field(..., description="Google Sheet ID")
    spreadsheet_title: str = Field(default="", description="Google Sheet title")
    message: str = Field(..., description="Status message")


class HoursSubmissionRequest(BaseModel):
    """Request model for submitting hours worked."""
    employee_name: str = Field(..., min_length=1, description="Employee name")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM format (24-hour)")
    end_time: str = Field(..., description="End time in HH:MM format (24-hour)")
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Ensure date is in valid format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        """Ensure time is in valid format."""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format (24-hour)")


class HoursSubmissionResponse(BaseModel):
    """Response model for hours submission."""
    success: bool = Field(..., description="Whether submission succeeded")
    message: str = Field(..., description="Status message")
    hours_worked: Optional[float] = Field(default=None, description="Calculated hours")
    date: str = Field(..., description="Date of submission")


class DailyTipRequest(BaseModel):
    """Request model for manager submitting daily tips."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_tips: float = Field(..., gt=0, description="Total tips collected for the day")
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Ensure date is in valid format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class DailyTipResponse(BaseModel):
    """Response model for daily tip submission."""
    success: bool = Field(..., description="Whether submission succeeded")
    message: str = Field(..., description="Status message")
    date: str = Field(..., description="Date of submission")
    total_tips: float = Field(..., description="Total tips amount")
    formulas_injected: bool = Field(..., description="Whether formulas were injected")

