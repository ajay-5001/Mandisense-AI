"""
MandiSense OpenWeather API Service
===================================
Fetches live weather reports and multi-day forecasts for regional mandis
using latitude/longitude coordinates and caches it in the database.
"""

import os
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.db.models import Region, Weather
from app.utils.http_client import get_async_client

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

class WeatherServiceError(Exception):
    """Custom exception class for weather service issues."""
    def __init__(self, message: str, status_code: int = 500, error_type: str = "GENERIC_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type

async def fetch_live_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches current weather and 5-day forecast from OpenWeather API.
    
    Raises:
        WeatherServiceError on API rate limits, authentication issues, or network failures.
    """
    key = os.getenv("OPENWEATHER_API_KEY", "") or OPENWEATHER_API_KEY
    if not key or "YOUR_OPENWEATHER" in key:
        raise WeatherServiceError("OpenWeather API key is missing or not configured.", 400, "MISSING_KEY")
        
    client = get_async_client()
    
    # 1. Fetch current weather
    current_url = f"{OPENWEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
    # 2. Fetch 5-day / 3-hour forecast
    forecast_url = f"{OPENWEATHER_BASE_URL}/forecast?lat={lat}&lon={lon}&appid={key}&units=metric"
    
    try:
        current_res = await client.get(current_url)
        forecast_res = await client.get(forecast_url)
        
        # Handle Rate Limit (429)
        if current_res.status_code == 429 or forecast_res.status_code == 429:
            raise WeatherServiceError("OpenWeather API rate limit exceeded. Please try again later.", 429, "RATE_LIMIT")
            
        # Handle Invalid Key (401)
        if current_res.status_code == 401 or forecast_res.status_code == 401:
            raise WeatherServiceError("Invalid OpenWeather API Key. Authentication failed.", 401, "INVALID_KEY")
            
        if current_res.status_code != 200 or forecast_res.status_code != 200:
            err_msg = current_res.text if current_res.status_code != 200 else forecast_res.text
            raise WeatherServiceError(f"OpenWeather API Error: {err_msg}", 503, "API_FAILURE")
            
        return {
            "current": current_res.json(),
            "forecast": forecast_res.json()
        }
    except httpx.RequestError as exc:
        raise WeatherServiceError(f"Network connectivity error while contacting OpenWeather: {exc}", 503, "NETWORK_FAILURE")
    except Exception as exc:
        if isinstance(exc, WeatherServiceError):
            raise exc
        raise WeatherServiceError(f"Unexpected error: {str(exc)}", 500, "GENERIC_ERROR")

# Let's import httpx locally inside the catch block if needed, or import at top
import httpx

async def update_region_weather(db: Session, region_id: int) -> bool:
    """
    Fetches real-time weather and forecast data for a region and upserts it in the local Weather table.
    
    Returns:
        True if updated successfully, False if skipped (falls back to synthetic data).
    """
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        return False
        
    try:
        weather_payload = await fetch_live_weather_data(region.latitude, region.longitude)
        
        # Process current weather (Today)
        current = weather_payload["current"]
        today_date = date.today()
        
        today_temp_min = current["main"].get("temp_min", current["main"]["temp"])
        today_temp_max = current["main"].get("temp_max", current["main"]["temp"])
        today_humidity = float(current["main"].get("humidity", 50))
        
        # OpenWeather returns rain volume in mm for 1h or 3h
        today_rain = 0.0
        if "rain" in current:
            today_rain = current["rain"].get("1h", current["rain"].get("3h", 0.0))
            
        _upsert_weather_record(
            db=db,
            region_id=region_id,
            target_date=today_date,
            temp_max=today_temp_max,
            temp_min=today_temp_min,
            humidity=today_humidity,
            rainfall_mm=today_rain
        )
        
        # Process forecast data (grouped by date)
        forecast_list = weather_payload["forecast"].get("list", [])
        daily_groups = {}
        
        for item in forecast_list:
            dt = datetime.fromtimestamp(item["dt"]).date()
            if dt == today_date:
                continue # Skip today as we used current weather API
                
            if dt not in daily_groups:
                daily_groups[dt] = []
            daily_groups[dt].append(item)
            
        for dt, items in daily_groups.items():
            temps = [x["main"]["temp"] for x in items]
            humidities = [x["main"]["humidity"] for x in items]
            
            t_min = min(temps) if temps else 25.0
            t_max = max(temps) if temps else 35.0
            avg_hum = sum(humidities) / len(humidities) if humidities else 60.0
            
            tot_rain = 0.0
            for item in items:
                if "rain" in item:
                    tot_rain += item["rain"].get("3h", 0.0)
                    
            _upsert_weather_record(
                db=db,
                region_id=region_id,
                target_date=dt,
                temp_max=t_max,
                temp_min=t_min,
                humidity=avg_hum,
                rainfall_mm=tot_rain
            )
            
        db.commit()
        return True
    except WeatherServiceError as e:
        # Gracefully handle keys/rates/network failures and let caller fallback
        print(f"[WeatherService] Skipped live weather update for region {region_id}: {e.message} ({e.error_type})")
        return False
    except Exception as e:
        print(f"[WeatherService] Unexpected error: {e}")
        return False

def _upsert_weather_record(
    db: Session,
    region_id: int,
    target_date: date,
    temp_max: float,
    temp_min: float,
    humidity: float,
    rainfall_mm: float
) -> None:
    """Helper method to insert or update a weather record in the SQLite DB."""
    rec = db.query(Weather).filter(Weather.region_id == region_id, Weather.date == target_date).first()
    if rec:
        rec.temp_max = round(temp_max, 1)
        rec.temp_min = round(temp_min, 1)
        rec.humidity = round(humidity, 1)
        rec.rainfall_mm = round(rainfall_mm, 1)
    else:
        db.add(Weather(
            region_id=region_id,
            date=target_date,
            temp_max=round(temp_max, 1),
            temp_min=round(temp_min, 1),
            humidity=round(humidity, 1),
            rainfall_mm=round(rainfall_mm, 1)
        ))
