"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


# --- Website Schemas ---

class WebsiteBase(BaseModel):
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None


class WebsiteCreate(WebsiteBase):
    pass


class WebsiteResponse(WebsiteBase):
    id: int
    screenshot_path: Optional[str] = None
    elo_rating: float
    matches_played: int
    wins: int
    losses: int
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


# --- Stats Schemas ---

class StatsResponse(BaseModel):
    total_websites: int
    total_comparisons: int
    avg_elo: float
