"""
SQLAlchemy models for Caesar ELO.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class Website(Base):
    """Represents a scraped website with its ELO rating."""
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
    
    # Metadata
    source = Column(String(255), nullable=True)  # e.g., "gmaps:restaurants:berlin"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
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
