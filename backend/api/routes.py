"""
API routes for Caesar ELO.
"""
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Website, Comparison
from schemas import (
    WebsiteCreate, 
    WebsiteResponse, 
    WebsiteLeaderboardItem,
    ComparisonPair, 
    ComparisonCreate, 
    ComparisonResponse,
    StatsResponse
)

router = APIRouter(prefix="/api", tags=["api"])


# --- Website Endpoints ---

@router.get("/websites", response_model=List[WebsiteResponse])
def list_websites(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List all websites."""
    websites = db.query(Website).offset(skip).limit(limit).all()
    return websites


@router.post("/websites", response_model=WebsiteResponse)
def create_website(website: WebsiteCreate, db: Session = Depends(get_db)):
    """Add a new website to the system."""
    # Check for duplicate URL
    existing = db.query(Website).filter(Website.url == website.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Website URL already exists")
    
    db_website = Website(**website.model_dump())
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website


@router.get("/websites/{website_id}", response_model=WebsiteResponse)
def get_website(website_id: int, db: Session = Depends(get_db)):
    """Get a specific website by ID."""
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    return website


# --- Comparison Endpoints ---

@router.get("/compare", response_model=ComparisonPair)
def get_comparison_pair(db: Session = Depends(get_db)):
    """Get two random websites for comparison."""
    # Get all website IDs
    websites = db.query(Website).all()
    
    if len(websites) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Need at least 2 websites to compare"
        )
    
    # Pick two random websites
    # TODO: Implement smarter matching (e.g., similar ELO ratings)
    selected = random.sample(websites, 2)
    
    return ComparisonPair(website_a=selected[0], website_b=selected[1])


@router.post("/compare", response_model=ComparisonResponse)
def submit_comparison(comparison: ComparisonCreate, db: Session = Depends(get_db)):
    """Submit a comparison result and update ELO ratings."""
    # Validate websites exist
    website_a = db.query(Website).filter(Website.id == comparison.website_a_id).first()
    website_b = db.query(Website).filter(Website.id == comparison.website_b_id).first()
    
    if not website_a or not website_b:
        raise HTTPException(status_code=404, detail="Website not found")
    
    if comparison.winner_id and comparison.winner_id not in [website_a.id, website_b.id]:
        raise HTTPException(status_code=400, detail="Winner must be one of the compared websites")
    
    # Calculate ELO changes
    # TODO: Implement actual ELO algorithm here (placeholder for codev)
    elo_change_a = 0.0
    elo_change_b = 0.0
    
    if comparison.winner_id:
        # Placeholder ELO calculation - replace with proper algorithm
        K = 32  # K-factor
        expected_a = 1 / (1 + 10 ** ((website_b.elo_rating - website_a.elo_rating) / 400))
        expected_b = 1 - expected_a
        
        if comparison.winner_id == website_a.id:
            elo_change_a = K * (1 - expected_a)
            elo_change_b = K * (0 - expected_b)
            website_a.wins += 1
            website_b.losses += 1
        else:
            elo_change_a = K * (0 - expected_a)
            elo_change_b = K * (1 - expected_b)
            website_a.losses += 1
            website_b.wins += 1
        
        website_a.elo_rating += elo_change_a
        website_b.elo_rating += elo_change_b
        website_a.matches_played += 1
        website_b.matches_played += 1
    
    # Record comparison
    db_comparison = Comparison(
        website_a_id=comparison.website_a_id,
        website_b_id=comparison.website_b_id,
        winner_id=comparison.winner_id,
        elo_change_a=elo_change_a,
        elo_change_b=elo_change_b
    )
    db.add(db_comparison)
    db.commit()
    db.refresh(db_comparison)
    
    return db_comparison


# --- Leaderboard ---

@router.get("/leaderboard", response_model=List[WebsiteLeaderboardItem])
def get_leaderboard(
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Get websites ranked by ELO rating."""
    websites = (
        db.query(Website)
        .order_by(Website.elo_rating.desc())
        .limit(limit)
        .all()
    )
    
    return [
        WebsiteLeaderboardItem(
            **{**website.__dict__, "rank": idx + 1}
        )
        for idx, website in enumerate(websites)
    ]


# --- Stats ---

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    total_websites = db.query(func.count(Website.id)).scalar() or 0
    total_comparisons = db.query(func.count(Comparison.id)).scalar() or 0
    avg_elo = db.query(func.avg(Website.elo_rating)).scalar() or 1000.0
    
    return StatsResponse(
        total_websites=total_websites,
        total_comparisons=total_comparisons,
        avg_elo=avg_elo
    )
