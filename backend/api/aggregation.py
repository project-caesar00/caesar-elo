"""
API routes for data aggregation (Google Places search).
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import SearchQuery, Place
from services.google_places import (
    aggregate_places,
    GooglePlacesError,
    QuotaExceededError
)

router = APIRouter(prefix="/api", tags=["aggregation"])


# --- Request/Response Schemas ---

class AggregationRequest(BaseModel):
    """Request schema for place aggregation."""
    query: str = Field(..., min_length=2, max_length=200, description="Search query (e.g. 'Sushi Berlin')")
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Minimum rating filter")


class PlaceResultSchema(BaseModel):
    """A single place result."""
    rank: int
    name: str
    rating_count: int
    rating_score: Optional[float]
    website_url: Optional[str]
    google_place_id: str


class AggregationResponse(BaseModel):
    """Response schema for place aggregation."""
    results: list[PlaceResultSchema]
    query: str
    total_count: int
    search_query_id: int  # ID der gespeicherten Suchanfrage


# --- Endpoints ---

@router.post("/aggregate", response_model=AggregationResponse)
async def aggregate_places_endpoint(
    request: AggregationRequest,
    db: Session = Depends(get_db)
):
    """
    Search for places using a text query and return sorted by review count.
    
    The results are fetched from Google Places API (New) using text search,
    with pagination to collect up to 60 results. Results are sorted by
    userRatingCount in descending order and saved to database.
    """
    try:
        result = await aggregate_places(
            query=request.query,
            min_rating=request.min_rating
        )
        
        # Speichere Suchanfrage in DB
        search_query = SearchQuery(
            query=request.query,
            min_rating=request.min_rating,
            results_count=result["total_count"]
        )
        db.add(search_query)
        db.flush()  # Um die ID zu bekommen
        
        # Speichere alle Places
        for place_data in result["results"]:
            place = Place(
                search_query_id=search_query.id,
                google_place_id=place_data["google_place_id"],
                name=place_data["name"],
                rating_count=place_data["rating_count"],
                rating_score=place_data["rating_score"],
                website_url=place_data["website_url"],
                rank=place_data["rank"]
            )
            db.add(place)
        
        db.commit()
        
        return {
            **result,
            "search_query_id": search_query.id
        }
    
    except QuotaExceededError:
        raise HTTPException(
            status_code=429,
            detail="API Limit erreicht, bitte später versuchen."
        )
    
    except GooglePlacesError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google Places API Fehler: {str(e)}"
        )
