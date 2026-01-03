"""
Google Maps scraper for discovering business websites.
Uses Google Maps Places API (New).
"""
import asyncio
import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import logging

from config import get_settings

logger = logging.getLogger(__name__)

# Get API key from config
settings = get_settings()

# Places API endpoints
PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Common business types for filtering
BUSINESS_TYPES = [
    "restaurant",
    "cafe",
    "bar",
    "gym",
    "spa",
    "beauty_salon",
    "hair_salon",
    "dentist",
    "doctor",
    "lawyer",
    "accounting",
    "real_estate_agency",
    "hotel",
    "car_dealer",
    "car_repair",
    "store",
    "clothing_store",
    "jewelry_store",
    "furniture_store",
    "home_goods_store",
    "pet_store",
    "florist",
    "bakery",
]


async def geocode_location(location: str) -> Optional[Dict[str, float]]:
    """Convert a location string to lat/lng coordinates."""
    if not settings.google_maps_api_key:
        logger.error("GOOGLE_MAPS_API_KEY not set")
        return None
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GEOCODE_URL,
            params={
                "address": location,
                "key": settings.google_maps_api_key
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Geocode failed: {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get("status") != "OK" or not data.get("results"):
            logger.error(f"Geocode returned no results for: {location}")
            return None
        
        location_data = data["results"][0]["geometry"]["location"]
        return {
            "latitude": location_data["lat"],
            "longitude": location_data["lng"]
        }


async def search_nearby_places(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    included_types: Optional[List[str]] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for places near a location using Places API (New).
    Returns list of places with their details.
    """
    if not settings.google_maps_api_key:
        logger.error("GOOGLE_MAPS_API_KEY not set")
        return []
    
    radius_meters = min(radius_km * 1000, 50000)  # Max 50km
    
    request_body = {
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        },
        "maxResultCount": min(max_results, 20)  # API limit
    }
    
    if included_types:
        request_body["includedTypes"] = included_types
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_maps_api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.primaryType,places.nationalPhoneNumber"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PLACES_NEARBY_URL,
            json=request_body,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Places API failed: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        return data.get("places", [])


def extract_website_data(place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract website data from a place result."""
    website_url = place.get("websiteUri")
    
    if not website_url:
        return None
    
    # Normalize URL
    parsed = urlparse(website_url)
    if not parsed.scheme:
        website_url = f"https://{website_url}"
    
    return {
        "url": website_url,
        "name": place.get("displayName", {}).get("text"),
        "address": place.get("formattedAddress"),
        "phone": place.get("nationalPhoneNumber"),
        "business_type": place.get("primaryType"),
        "gmaps_place_id": place.get("id"),
    }


async def scrape_websites_from_location(
    location: str,
    radius_km: float = 10.0,
    business_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Main function to scrape websites from a location.
    
    Args:
        location: City or address to search around
        radius_km: Search radius in kilometers (max 50)
        business_types: List of business types to filter by
    
    Returns:
        List of website data dictionaries
    """
    # Geocode location
    coords = await geocode_location(location)
    if not coords:
        return []
    
    # Search for places
    places = await search_nearby_places(
        latitude=coords["latitude"],
        longitude=coords["longitude"],
        radius_km=radius_km,
        included_types=business_types
    )
    
    # Extract websites
    websites = []
    for place in places:
        website_data = extract_website_data(place)
        if website_data:
            websites.append(website_data)
    
    return websites


# Sync wrapper for use in FastAPI background tasks
def scrape_websites_sync(
    location: str,
    radius_km: float = 10.0,
    business_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Synchronous wrapper for scraping."""
    return asyncio.run(
        scrape_websites_from_location(location, radius_km, business_types)
    )


# Screenshot capture placeholder
async def capture_screenshot(url: str, output_path: str) -> bool:
    """
    Capture a screenshot of a website.
    
    TODO: Implement with Playwright
    For now, returns False (not implemented)
    """
    logger.warning("Screenshot capture not implemented yet")
    return False
