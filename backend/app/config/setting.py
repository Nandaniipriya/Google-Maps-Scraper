from pydantic import BaseModel
from typing import List, Optional

class SearchQuery(BaseModel):
    query: str

class Location(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    google_maps_url: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    business_status: Optional[str] = None
    address: Optional[str] = None
    total_reviews: Optional[str] = None
    booking_links: Optional[str] = None
    rating: Optional[str] = None
    hours: Optional[str] = None

class ScraperResponse(BaseModel):
    total_results: int
    locations: List[Location]