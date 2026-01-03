"""
Configuration management for Caesar ELO.
Loads settings from environment variables.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Google Maps API
    google_maps_api_key: str = ""
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # JWT
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 1 week
    
    # Database
    database_url: str = "sqlite:///./caesar_elo.db"
    
    # Frontend
    frontend_url: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
