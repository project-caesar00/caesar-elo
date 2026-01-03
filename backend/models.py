"""
SQLAlchemy models for Caesar ELO.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from database import Base


class Website(Base):
    """Represents a scraped website with its ELO rating and classification."""
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, nullable=False)
    name = Column(String(255), nullable=True)  # Business name from GMaps
    description = Column(Text, nullable=True)
    screenshot_path = Column(String(512), nullable=True)
    
    # ELO rating - starts at 1000
    elo_rating = Column(Float, default=1000.0, nullable=False)
    matches_played = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    
    # Classification flags
    is_designvorlage = Column(Boolean, default=False, nullable=False)  # Design template reference
    is_good_lead = Column(Boolean, default=False, nullable=False)  # Potential customer
    is_graded = Column(Boolean, default=False, nullable=False)  # Has been reviewed
    graded_at = Column(DateTime, nullable=True)
    
    # Metadata
    source = Column(String(255), nullable=True)  # e.g., "gmaps:restaurants:berlin"
    gmaps_place_id = Column(String(255), nullable=True)  # Google Maps Place ID
    business_type = Column(String(255), nullable=True)  # e.g., "restaurant", "gym"
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    grades = relationship("WebsiteGrade", back_populates="website", uselist=False)
    comparisons_as_a = relationship(
        "Comparison", 
        foreign_keys="Comparison.website_a_id",
        back_populates="website_a"
    )
    comparisons_as_b = relationship(
        "Comparison", 
        foreign_keys="Comparison.website_b_id",
        back_populates="website_b"
    )


class WebsiteGrade(Base):
    """Stores Likert-scale grades for a website's visual aspects."""
    __tablename__ = "website_grades"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False, unique=True)
    
    # Likert scale grades (1-5)
    overall_aesthetic = Column(Integer, nullable=True)
    color_harmony = Column(Integer, nullable=True)
    typography_quality = Column(Integer, nullable=True)
    layout_spacing = Column(Integer, nullable=True)
    imagery_quality = Column(Integer, nullable=True)
    visual_hierarchy = Column(Integer, nullable=True)
    mobile_responsiveness = Column(Integer, nullable=True)
    
    # Notes per field for taxonomy examples (JSON: {"field_name": "note text"})
    notes = Column(JSON, nullable=True, default=dict)
    
    # General comments
    general_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    website = relationship("Website", back_populates="grades")


class Comparison(Base):
    """Records a single comparison between two websites."""
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    
    website_a_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    website_b_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    winner_id = Column(Integer, ForeignKey("websites.id"), nullable=True)  # NULL = skip/draw
    
    # ELO changes recorded for history
    elo_change_a = Column(Float, nullable=True)
    elo_change_b = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    website_a = relationship("Website", foreign_keys=[website_a_id], back_populates="comparisons_as_a")
    website_b = relationship("Website", foreign_keys=[website_b_id], back_populates="comparisons_as_b")
    winner = relationship("Website", foreign_keys=[winner_id])


class ScrapeJob(Base):
    """Tracks Google Maps scraping jobs."""
    __tablename__ = "scrape_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Search parameters
    location = Column(String(255), nullable=False)  # City/address
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=10.0)
    business_types = Column(JSON, nullable=True)  # List of types
    
    # Status
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    websites_found = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
