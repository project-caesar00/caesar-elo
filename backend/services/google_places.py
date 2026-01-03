"""
Google Places API Text Search Service.
Implements text-based search with pagination for restaurant aggregation.
"""
import httpx
import logging
from typing import List, Optional, Dict, Any

from config import get_settings

logger = logging.getLogger(__name__)

# Text Search API endpoint (New Places API)
TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Field mask for cost optimization - only request needed fields
FIELD_MASK = "places.id,places.displayName,places.userRatingCount,places.rating,places.websiteUri"


class PlaceResult:
    """Represents a single place from search results."""
    
    def __init__(
        self,
        google_place_id: str,
        name: str,
        rating_count: int,
        rating_score: Optional[float],
        website_url: Optional[str],
        rank: int = 0
    ):
        self.google_place_id = google_place_id
        self.name = name
        self.rating_count = rating_count
        self.rating_score = rating_score
        self.website_url = website_url
        self.rank = rank
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "name": self.name,
            "rating_count": self.rating_count,
            "rating_score": self.rating_score,
            "website_url": self.website_url,
            "google_place_id": self.google_place_id
        }


class GooglePlacesError(Exception):
    """Custom exception for Google Places API errors."""
    pass


class QuotaExceededError(GooglePlacesError):
    """Raised when API quota is exceeded."""
    pass


async def search_places_text(
    query: str,
    min_rating: Optional[float] = None,
    max_results: int = 60,
    language_code: str = "de"
) -> List[PlaceResult]:
    """
    Search for places using text query with pagination.
    
    Args:
        query: Search query (e.g., "Asiatisch Potsdam")
        min_rating: Optional minimum rating filter (1.0-5.0)
        max_results: Maximum number of results to fetch (default 60)
        language_code: Language for results (default "de")
    
    Returns:
        List of PlaceResult sorted by userRatingCount descending
    
    Raises:
        GooglePlacesError: If API call fails
        QuotaExceededError: If API quota is exceeded
    """
    settings = get_settings()
    
    if not settings.google_maps_api_key:
        raise GooglePlacesError("GOOGLE_MAPS_API_KEY not configured")
    
    all_places: List[PlaceResult] = []
    next_page_token: Optional[str] = None
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_maps_api_key,
        "X-Goog-FieldMask": FIELD_MASK
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while len(all_places) < max_results:
            # Build request body
            request_body: Dict[str, Any] = {
                "textQuery": query,
                "languageCode": language_code,
            }
            
            if min_rating is not None:
                request_body["minRating"] = min_rating
            
            if next_page_token:
                request_body["pageToken"] = next_page_token
            
            logger.info(f"Searching places: query='{query}', page_token={bool(next_page_token)}")
            
            try:
                response = await client.post(
                    TEXT_SEARCH_URL,
                    json=request_body,
                    headers=headers
                )
            except httpx.TimeoutException:
                raise GooglePlacesError("API request timed out")
            except httpx.RequestError as e:
                raise GooglePlacesError(f"API request failed: {e}")
            
            # Handle error responses
            if response.status_code == 429:
                raise QuotaExceededError("API quota exceeded - please try again later")
            
            if response.status_code != 200:
                error_detail = response.text[:200] if response.text else "Unknown error"
                logger.error(f"Places API error: {response.status_code} - {error_detail}")
                raise GooglePlacesError(f"API error ({response.status_code}): {error_detail}")
            
            data = response.json()
            places = data.get("places", [])
            
            # Parse results
            for place in places:
                display_name = place.get("displayName", {})
                name = display_name.get("text", "Unknown")
                
                result = PlaceResult(
                    google_place_id=place.get("id", ""),
                    name=name,
                    rating_count=place.get("userRatingCount", 0),
                    rating_score=place.get("rating"),
                    website_url=place.get("websiteUri")
                )
                all_places.append(result)
            
            logger.info(f"Fetched {len(places)} places, total: {len(all_places)}")
            
            # Check for next page
            next_page_token = data.get("nextPageToken")
            
            if not next_page_token or len(places) == 0:
                break
    
    # Sort by rating count descending
    all_places.sort(key=lambda p: p.rating_count, reverse=True)
    
    # Assign ranks
    for idx, place in enumerate(all_places):
        place.rank = idx + 1
    
    return all_places[:max_results]


async def aggregate_places(
    query: str,
    min_rating: Optional[float] = None
) -> Dict[str, Any]:
    """
    Main aggregation function - fetches and sorts places.
    
    Returns dict with results, query, and total count.
    """
    places = await search_places_text(
        query=query,
        min_rating=min_rating,
        max_results=60
    )
    
    return {
        "results": [p.to_dict() for p in places],
        "query": query,
        "total_count": len(places)
    }
