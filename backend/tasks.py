"""
Background tasks for Caesar ELO.
Handles async scraping and website processing.
"""
import asyncio
from datetime import datetime
from typing import Optional
import logging

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Website, ScrapeJob
from scraper import scrape_websites_from_location

logger = logging.getLogger(__name__)


def run_scrape_job(job_id: int):
    """
    Execute a scraping job in the background.
    This function is designed to be run in a background thread.
    """
    db = SessionLocal()
    try:
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if not job:
            logger.error(f"Scrape job {job_id} not found")
            return
        
        # Update status to running
        job.status = "running"
        db.commit()
        
        # Run the async scraper
        websites_data = asyncio.run(
            scrape_websites_from_location(
                location=job.location,
                radius_km=job.radius_km,
                business_types=job.business_types
            )
        )
        
        # Store coordinates if we got results
        if websites_data:
            # We could store lat/lng on the job here if needed
            pass
        
        # Add websites to database
        websites_added = 0
        for website_data in websites_data:
            # Check for duplicate URL
            existing = db.query(Website).filter(Website.url == website_data["url"]).first()
            if existing:
                continue
            
            website = Website(
                url=website_data["url"],
                name=website_data.get("name"),
                address=website_data.get("address"),
                phone=website_data.get("phone"),
                business_type=website_data.get("business_type"),
                gmaps_place_id=website_data.get("gmaps_place_id"),
                source=f"gmaps:{job.location}:{','.join(job.business_types or [])}"
            )
            db.add(website)
            websites_added += 1
        
        # Update job status
        job.status = "completed"
        job.websites_found = websites_added
        job.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Scrape job {job_id} completed: {websites_added} websites added")
        
    except Exception as e:
        logger.exception(f"Scrape job {job_id} failed: {e}")
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()
