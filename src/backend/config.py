"""
Configuration management for the Vila Acadia backend.
Loads environment variables and validates required settings.
"""
import json
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    google_sheet_id: str = Field(..., env="GOOGLE_SHEET_ID")
    service_account_json: str = Field(..., env="SERVICE_ACCOUNT_JSON")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Frontend URL for CORS configuration
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    # Additional allowed origins (comma-separated)
    allowed_origins: str = Field(default="", env="ALLOWED_ORIGINS")
    
    # Manager authentication
    manager_password: str = Field(default="manager2024", env="MANAGER_PASSWORD")
    
    @field_validator("service_account_json")
    @classmethod
    def validate_service_account_json(cls, v: str) -> str:
        """Validate that service account JSON is properly formatted."""
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError:
            raise ValueError("SERVICE_ACCOUNT_JSON must be valid JSON")
    
    def get_service_account_dict(self) -> Dict[str, Any]:
        """Parse and return service account credentials as a dictionary."""
        return json.loads(self.service_account_json)
    
    def get_allowed_origins(self) -> list[str]:
        """Get list of allowed CORS origins."""
        origins = [self.frontend_url]
        
        # Add additional origins from comma-separated string
        if self.allowed_origins:
            additional = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
            origins.extend(additional)
        
        return origins
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
# For testing: this will be lazy-loaded if environment variables are not set
_settings = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Initialize settings on import
settings = Settings()


