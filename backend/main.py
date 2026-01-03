"""
Caesar ELO - Website Rating System
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import engine, Base
from api.routes import router as api_router
from api.auth import router as auth_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Caesar ELO",
    description="ELO-based website rating system for scraped Google Maps sites",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for screenshots (create dir if not exists)
SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=SCREENSHOTS_DIR), name="screenshots")

# Include API routes
app.include_router(api_router)
app.include_router(auth_router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "caesar-elo"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
