"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


# --- Website Schemas ---

class WebsiteBase(BaseModel):
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    business_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class WebsiteCreate(WebsiteBase):
    gmaps_place_id: Optional[str] = None


class WebsiteResponse(WebsiteBase):
    id: int
    screenshot_path: Optional[str] = None
    elo_rating: float
    matches_played: int
    wins: int
    losses: int
    is_designvorlage: bool
    is_good_lead: bool
    is_graded: bool
    graded_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WebsiteLeaderboardItem(BaseModel):
    id: int
    url: str
    name: Optional[str]
    screenshot_path: Optional[str]
    elo_rating: float
    matches_played: int
    wins: int
    losses: int
    rank: int

    class Config:
        from_attributes = True


# --- Grading Schemas ---

class WebsiteGradeCreate(BaseModel):
    """Submit grades for a website."""
    overall_aesthetic: Optional[int] = Field(None, ge=1, le=5)
    color_harmony: Optional[int] = Field(None, ge=1, le=5)
    typography_quality: Optional[int] = Field(None, ge=1, le=5)
    layout_spacing: Optional[int] = Field(None, ge=1, le=5)
    imagery_quality: Optional[int] = Field(None, ge=1, le=5)
    visual_hierarchy: Optional[int] = Field(None, ge=1, le=5)
    mobile_responsiveness: Optional[int] = Field(None, ge=1, le=5)
    
    notes: Optional[Dict[str, str]] = None  # {"field_name": "note text"}
    general_comment: Optional[str] = None
    
    # Flags
    is_designvorlage: bool = False
    is_good_lead: bool = False


class WebsiteGradeResponse(BaseModel):
    id: int
    website_id: int
    overall_aesthetic: Optional[int]
    color_harmony: Optional[int]
    typography_quality: Optional[int]
    layout_spacing: Optional[int]
    imagery_quality: Optional[int]
    visual_hierarchy: Optional[int]
    mobile_responsiveness: Optional[int]
    notes: Optional[Dict[str, str]]
    general_comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WebsiteWithGrade(WebsiteResponse):
    """Website with its grades included."""
    grades: Optional[WebsiteGradeResponse] = None


# --- Comparison Schemas ---

class ComparisonPair(BaseModel):
    """Two websites to compare."""
    website_a: WebsiteResponse
    website_b: WebsiteResponse


class ComparisonCreate(BaseModel):
    """Submit a comparison result."""
    website_a_id: int
    website_b_id: int
    winner_id: Optional[int] = None  # NULL = skip


class ComparisonResponse(BaseModel):
    id: int
    website_a_id: int
    website_b_id: int
    winner_id: Optional[int]
    elo_change_a: Optional[float]
    elo_change_b: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Scraping Schemas ---

class ScrapeConfigCreate(BaseModel):
    """Configuration for a scraping job."""
    location: str  # City or address
    radius_km: float = Field(default=10.0, ge=0.1, le=50.0)
    business_types: List[str] = []  # e.g., ["restaurant", "gym"]


class ScrapeJobResponse(BaseModel):
    id: int
    location: str
    radius_km: float
    business_types: Optional[List[str]]
    status: str
    websites_found: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Stats Schemas ---

class StatsResponse(BaseModel):
    total_websites: int
    total_comparisons: int
    total_graded: int
    total_designvorlage: int
    total_good_leads: int
    avg_elo: float


# --- Stack Review Schemas ---

class StackStats(BaseModel):
    """Stats for the grading stack."""
    ungraded_count: int
    graded_count: int
    designvorlage_count: int
    good_lead_count: int
