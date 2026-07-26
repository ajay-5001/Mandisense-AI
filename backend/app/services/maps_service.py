"""
MandiSense Google Maps API Service
===================================
Provides geocoding, location coordinates lookup, and closest mandi calculations.
"""

import os
import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models import Region
from app.utils.http_client import get_async_client

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

class MapsServiceError(Exception):
    """Custom exception class for Maps service issues."""
    def __init__(self, message: str, status_code: int = 500, error_type: str = "GENERIC_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes the geodesic distance in kilometers between two lat/lng coordinates."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def geocode_address(address: str) -> Dict[str, Any]:
    """
    Geocodes an address into latitude, longitude, and formatted text.
    
    Returns a mock fallback coordinate if Google Maps API key is not configured.
    """
    key = os.getenv("GOOGLE_MAPS_API_KEY", "") or GOOGLE_MAPS_API_KEY
    
    address_lower = address.lower()
    fallback_data = {
        "latitude": 28.7041,
        "longitude": 77.1025,
        "formatted_address": f"{address} (Mocked Azadpur, Delhi)"
    }
    
    if "delhi" in address_lower or "azadpur" in address_lower:
        fallback_data = {"latitude": 28.7041, "longitude": 77.1025, "formatted_address": "Azadpur, Delhi, India"}
    elif "mumbai" in address_lower or "vashi" in address_lower:
        fallback_data = {"latitude": 19.0760, "longitude": 72.8777, "formatted_address": "Vashi, Mumbai, Maharashtra, India"}
    elif "chennai" in address_lower or "koyambedu" in address_lower:
        fallback_data = {"latitude": 13.0827, "longitude": 80.2707, "formatted_address": "Koyambedu, Chennai, Tamil Nadu, India"}
        
    if not key or "YOUR_GOOGLE_MAPS" in key:
        print(f"[MapsService] Google Maps API key is not configured. Returning fallback for: {address}")
        return fallback_data
        
    client = get_async_client()
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={key}"
    
    try:
        res = await client.get(url)
        if res.status_code != 200:
            print(f"[MapsService] Google Maps API failed with status {res.status_code}. Returning fallback.")
            return fallback_data
            
        data = res.json()
        status = data.get("status")
        
        if status == "OK" and data.get("results"):
            result = data["results"][0]
            loc = result["geometry"]["location"]
            return {
                "latitude": loc["lat"],
                "longitude": loc["lng"],
                "formatted_address": result.get("formatted_address", address)
            }
        else:
            print(f"[MapsService] Google Maps API status error: {status}. Returning fallback.")
            return fallback_data
            
    except Exception as exc:
        print(f"[MapsService] Unexpected error: {str(exc)}. Returning fallback.")
        return fallback_data

import httpx

async def get_nearby_mandis(db: Session, lat: float, lng: float, radius_km: float = 200.0) -> List[Dict[str, Any]]:
    """
    Finds the closest agricultural mandis from the database based on coordinates.
    Filters by distance and returns a sorted list.
    """
    regions = db.query(Region).all()
    results = []
    
    for r in regions:
        distance = haversine_distance(lat, lng, r.latitude, r.longitude)
        if distance <= radius_km:
            results.append({
                "id": r.id,
                "name": r.name,
                "state": r.state,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "distance_km": round(distance, 1)
            })
            
    # Sort closest first
    results.sort(key=lambda x: x["distance_km"])
    return results
