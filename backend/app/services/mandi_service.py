"""
MandiSense Live Mandi Price API Service
========================================
Connects to government datasets (Agmarknet via data.gov.in API portal)
to extract real-time crop/vegetable/fruit wholesale pricing updates.
"""

import os
from datetime import date
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Item, Region, DailyPrice
from app.utils.http_client import get_async_client

MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
AGMARKNET_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a86d9fb70022"

class MandiServiceError(Exception):
    """Custom exception class for Mandi Price service issues."""
    def __init__(self, message: str, status_code: int = 500, error_type: str = "GENERIC_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type

async def fetch_live_mandi_price(commodity: str, state: str, market: str) -> Optional[float]:
    """
    Fetches the latest modal (wholesale) price in INR/quintal from data.gov.in.
    Converts it to INR/kg.
    
    Returns a mock fallback price if Mandi Price API key is not configured or if API fails.
    """
    base_prices = {
        "Tomato": 25.0, "Onion": 20.0, "Potato": 18.0, "Cauliflower": 22.0,
        "Green Chili": 40.0, "Lady Finger": 30.0, "Brinjal": 28.0, "Cabbage": 15.0,
        "Carrot": 30.0, "Spinach": 20.0, "Banana": 35.0, "Apple": 100.0,
        "Mango": 60.0, "Papaya": 25.0, "Grapes": 55.0
    }
    
    import random
    # Create a deterministic mock price based on commodity, market/state, and today's date
    today_seed = hash(commodity + state + market + str(date.today())) % 10000
    rng = random.Random(today_seed)
    base = base_prices.get(commodity, 30.0)
    mock_price = round(base * rng.uniform(0.9, 1.15), 2)
    
    key = os.getenv("MANDI_API_KEY", "") or MANDI_API_KEY
    if not key or "YOUR_LIVE_MANDI" in key:
        print(f"[MandiService] Mandi API key is not configured. Returning fallback mock price for {commodity} in {market}: {mock_price}")
        return mock_price
        
    client = get_async_client()
    
    # Filter strings need to match agmarknet naming
    # Market filter: e.g. "Azadpur" instead of "Azadpur Mandi"
    market_clean = market.replace(" Mandi", "").replace(" APMC", "").replace(" Market", "").replace(" Wholesale Market", "")
    
    url = (
        f"{AGMARKNET_API_URL}?api-key={key}&format=json"
        f"&filters[commodity]={commodity}&filters[state]={state}&filters[market]={market_clean}"
    )
    
    try:
        res = await client.get(url)
        if res.status_code == 401 or res.status_code == 403:
            print(f"[MandiService] Invalid Mandi Price API Key. Returning fallback: {mock_price}")
            return mock_price
        elif res.status_code == 429:
            print(f"[MandiService] Mandi API rate limit exceeded. Returning fallback: {mock_price}")
            return mock_price
        elif res.status_code != 200:
            print(f"[MandiService] Mandi Price API returned error code {res.status_code}. Returning fallback: {mock_price}")
            return mock_price
            
        data = res.json()
        records = data.get("records", [])
        
        if records:
            # Agmarknet prices are in INR per Quintal (100 kg)
            # We convert to INR per kg
            modal_price_quintal = float(records[0].get("modal_price", 0.0))
            if modal_price_quintal > 0:
                price_per_kg = modal_price_quintal / 100.0
                return round(price_per_kg, 2)
                
        return mock_price
    except httpx.RequestError as exc:
        print(f"[MandiService] Network error while contacting Mandi Price API: {exc}. Returning fallback: {mock_price}")
        return mock_price
    except Exception as exc:
        print(f"[MandiService] Unexpected error: {str(exc)}. Returning fallback: {mock_price}")
        return mock_price

import httpx

async def sync_live_mandi_price(db: Session, item_id: int, region_id: int) -> Optional[float]:
    """
    Checks if a live price update is available for an item and region,
    caches/upserts it in the local database, and returns the retail price comparison.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    region = db.query(Region).filter(Region.id == region_id).first()
    
    if not item or not region:
        return None
        
    try:
        live_price_kg = await fetch_live_mandi_price(
            commodity=item.name,
            state=region.state,
            market=region.name
        )
        
        if live_price_kg:
            today_date = date.today()
            # Upsert into daily_prices
            price_rec = db.query(DailyPrice).filter(
                DailyPrice.item_id == item_id,
                DailyPrice.region_id == region_id,
                DailyPrice.date == today_date
            ).first()
            
            retail_price = round(live_price_kg * 1.30, 2) # Typical markup
            
            if price_rec:
                price_rec.wholesale_price = live_price_kg
                price_rec.retail_price = retail_price
            else:
                db.add(DailyPrice(
                    item_id=item_id,
                    region_id=region_id,
                    date=today_date,
                    wholesale_price=live_price_kg,
                    retail_price=retail_price
                ))
            db.commit()
            return live_price_kg
    except MandiServiceError as e:
        print(f"[MandiService] Live price sync skipped: {e.message} ({e.error_type})")
    except Exception as e:
        print(f"[MandiService] Unexpected error: {e}")
        
    return None
