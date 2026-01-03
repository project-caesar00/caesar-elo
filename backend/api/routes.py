"""
API routes for Caesar ELO.
"""
import random
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Website, Comparison, WebsiteGrade, ScrapeJob
from schemas import (
    WebsiteCreate, 
    WebsiteResponse,
    WebsiteWithGrade,
    WebsiteLeaderboardItem,
    WebsiteGradeCreate,
    WebsiteGradeResponse,
    ComparisonPair, 
    ComparisonCreate, 
    ComparisonResponse,
    ScrapeConfigCreate,
    ScrapeJobResponse,
    StatsResponse,
    StackStats
)
from tasks import run_scrape_job

router = APIRouter(prefix="/api", tags=["api"])


# --- Website Endpoints ---

@router.get("/websites", response_model=List[WebsiteResponse])
def list_websites(
    skip: int = 0, 
    limit: int = 100,
    is_graded: Optional[bool] = None,
    is_designvorlage: Optional[bool] = None,
    is_good_lead: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all websites with optional filters."""
    query = db.query(Website)
    
    if is_graded is not None:
        query = query.filter(Website.is_graded == is_graded)
    if is_designvorlage is not None:
        query = query.filter(Website.is_designvorlage == is_designvorlage)
    if is_good_lead is not None:
        query = query.filter(Website.is_good_lead == is_good_lead)
    
    websites = query.offset(skip).limit(limit).all()
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


@router.get("/websites/{website_id}", response_model=WebsiteWithGrade)
def get_website(website_id: int, db: Session = Depends(get_db)):
    """Get a specific website by ID with its grades."""
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    return website


# --- Stack Review Endpoints ---

@router.get("/stack/next", response_model=Optional[WebsiteResponse])
def get_next_ungraded(db: Session = Depends(get_db)):
    """Get the next ungraded website from the stack."""
    website = (
        db.query(Website)
        .filter(Website.is_graded == False)
        .order_by(Website.created_at.asc())
        .first()
    )
    return website


@router.get("/stack/stats", response_model=StackStats)
def get_stack_stats(db: Session = Depends(get_db)):
    """Get stats about the grading stack."""
    return StackStats(
        ungraded_count=db.query(func.count(Website.id)).filter(Website.is_graded == False).scalar() or 0,
        graded_count=db.query(func.count(Website.id)).filter(Website.is_graded == True).scalar() or 0,
        designvorlage_count=db.query(func.count(Website.id)).filter(Website.is_designvorlage == True).scalar() or 0,
        good_lead_count=db.query(func.count(Website.id)).filter(Website.is_good_lead == True).scalar() or 0,
    )


@router.post("/websites/{website_id}/grade", response_model=WebsiteGradeResponse)
def grade_website(website_id: int, grade: WebsiteGradeCreate, db: Session = Depends(get_db)):
    """Submit grades for a website."""
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Check if already graded
    existing_grade = db.query(WebsiteGrade).filter(WebsiteGrade.website_id == website_id).first()
    
    if existing_grade:
        # Update existing grade
        for field in ['overall_aesthetic', 'color_harmony', 'typography_quality', 
                      'layout_spacing', 'imagery_quality', 'visual_hierarchy', 'mobile_responsiveness']:
            value = getattr(grade, field)
            if value is not None:
                setattr(existing_grade, field, value)
        
        if grade.notes is not None:
            existing_grade.notes = grade.notes
        if grade.general_comment is not None:
            existing_grade.general_comment = grade.general_comment
        
        existing_grade.updated_at = datetime.utcnow()
        db_grade = existing_grade
    else:
        # Create new grade
        db_grade = WebsiteGrade(
            website_id=website_id,
            overall_aesthetic=grade.overall_aesthetic,
            color_harmony=grade.color_harmony,
            typography_quality=grade.typography_quality,
            layout_spacing=grade.layout_spacing,
            imagery_quality=grade.imagery_quality,
            visual_hierarchy=grade.visual_hierarchy,
            mobile_responsiveness=grade.mobile_responsiveness,
            notes=grade.notes or {},
            general_comment=grade.general_comment
        )
        db.add(db_grade)
    
    # Update website flags
    website.is_designvorlage = grade.is_designvorlage
    website.is_good_lead = grade.is_good_lead
    website.is_graded = True
    website.graded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_grade)
    
    return db_grade


@router.post("/websites/{website_id}/skip")
def skip_website(website_id: int, db: Session = Depends(get_db)):
    """Skip a website without grading (marks as reviewed but not classified)."""
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    website.is_graded = True
    website.graded_at = datetime.utcnow()
    db.commit()
    
    return {"status": "skipped", "website_id": website_id}


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
    elo_change_a = 0.0
    elo_change_b = 0.0
    
    if comparison.winner_id:
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


# --- Scraping Endpoints ---

@router.post("/scrape", response_model=ScrapeJobResponse)
def start_scrape_job(
    config: ScrapeConfigCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new Google Maps scraping job."""
    # Create scrape job record
    job = ScrapeJob(
        location=config.location,
        radius_km=config.radius_km,
        business_types=config.business_types,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Trigger background scraping task
    background_tasks.add_task(run_scrape_job, job.id)
    
    return job


@router.get("/scrape/jobs", response_model=List[ScrapeJobResponse])
def list_scrape_jobs(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List recent scraping jobs."""
    jobs = (
        db.query(ScrapeJob)
        .order_by(ScrapeJob.created_at.desc())
        .limit(limit)
        .all()
    )
    return jobs


@router.get("/scrape/jobs/{job_id}", response_model=ScrapeJobResponse)
def get_scrape_job(job_id: int, db: Session = Depends(get_db)):
    """Get status of a specific scraping job."""
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scrape job not found")
    return job


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
    total_graded = db.query(func.count(Website.id)).filter(Website.is_graded == True).scalar() or 0
    total_designvorlage = db.query(func.count(Website.id)).filter(Website.is_designvorlage == True).scalar() or 0
    total_good_leads = db.query(func.count(Website.id)).filter(Website.is_good_lead == True).scalar() or 0
    avg_elo = db.query(func.avg(Website.elo_rating)).scalar() or 1000.0
    
    return StatsResponse(
        total_websites=total_websites,
        total_comparisons=total_comparisons,
        total_graded=total_graded,
        total_designvorlage=total_designvorlage,
        total_good_leads=total_good_leads,
        avg_elo=avg_elo
    )
