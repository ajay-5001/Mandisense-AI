"""
MandiSense Spoilage Risk Scoring Module
========================================
Computes a composite spoilage risk score (0-100) for each item
in each region on a given day.

Risk factors and weights:
    - Temperature (25%): Higher temp → faster spoilage
    - Humidity (25%):     High humidity → fungal growth, faster decay
    - Shelf life (30%):   Items closer to shelf-life expiry have higher risk
    - Oversupply (20%):   If supply exceeds forecasted demand, unsold stock spoils

Risk levels:
    🟢 0-33:   Low risk    — sell at normal price
    🟡 34-66:  Moderate    — consider price reduction
    🔴 67-100: High risk   — aggressive discount or dump stock

This is the KEY input for the recommendation engine in Phase 2.
"""

import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.database import SessionLocal
from app.db.models import Item, Weather, SalesVolume
from app.config import (
    RISK_WEIGHT_TEMPERATURE,
    RISK_WEIGHT_HUMIDITY,
    RISK_WEIGHT_SHELF_LIFE,
    RISK_WEIGHT_OVERSUPPLY,
    RISK_LOW_THRESHOLD,
    RISK_MODERATE_THRESHOLD,
)


def get_risk_level(score: float) -> dict:
    """Convert numeric risk score to a labeled risk level."""
    if score <= RISK_LOW_THRESHOLD:
        return {"level": "low", "label": "Low Risk", "color": "green", "emoji": "🟢"}
    elif score <= RISK_MODERATE_THRESHOLD:
        return {"level": "moderate", "label": "Moderate Risk", "color": "yellow", "emoji": "🟡"}
    else:
        return {"level": "high", "label": "High Risk", "color": "red", "emoji": "🔴"}


def _temperature_score(temp_max: float) -> float:
    """
    Temperature risk: higher temp → faster spoilage.
    
    Scoring:
    - Below 20°C: 0 (minimal spoilage risk from heat)
    - 20-40°C: linear scale 0-100
    - Above 40°C: capped at 100
    """
    if temp_max <= 20:
        return 0.0
    return min(100.0, (temp_max - 20) * 5.0)


def _humidity_score(humidity: float) -> float:
    """
    Humidity risk: high humidity → fungal growth, accelerated decay.
    
    Scoring:
    - Below 40%: 0 (dry conditions, low risk)
    - 40-90%: linear scale 0-100
    - Above 90%: capped at 100
    """
    if humidity <= 40:
        return 0.0
    return min(100.0, (humidity - 40) * 2.0)


def _shelf_life_score(shelf_life_days: int, days_since_harvest: int = 1) -> float:
    """
    Shelf life risk: closer to expiry → higher risk.
    
    Assumes fresh stock arrives daily (days_since_harvest=1 by default).
    For multi-day inventory tracking, this parameter can be adjusted.
    
    Scoring:
    - Full shelf life remaining: 0
    - No shelf life remaining: 100
    """
    if shelf_life_days <= 0:
        return 100.0
    remaining_ratio = max(0, (shelf_life_days - days_since_harvest)) / shelf_life_days
    return (1 - remaining_ratio) * 100.0


def _oversupply_score(yesterday_volume: float, forecasted_demand: float) -> float:
    """
    Oversupply risk: if supply exceeds demand, unsold stock will spoil.
    
    Scoring:
    - Demand > supply: 0 (stock will sell out)
    - Supply > demand by 50%+: 100
    """
    if forecasted_demand <= 0:
        return 80.0  # No demand data = risky
    
    ratio = yesterday_volume / forecasted_demand
    if ratio <= 1.0:
        return 0.0  # Demand meets or exceeds supply
    return min(100.0, (ratio - 1.0) * 200.0)  # 1.5x supply = score 100


def compute_spoilage_risk(
    item_id: int,
    region_id: int,
    target_date: date = None,
    days_since_harvest: int = 1,
    forecasted_demand: float = None,
) -> dict:
    """
    Compute the composite spoilage risk score for an item in a region.
    
    Args:
        item_id: Item ID from the database
        region_id: Region ID from the database
        target_date: Date to compute risk for (defaults to latest data date)
        days_since_harvest: How many days since the stock was harvested (default=1)
        forecasted_demand: Expected demand from forecast module. If None, 
                          uses yesterday's volume as a proxy.
    
    Returns:
        {
            "item_id": int,
            "region_id": int,
            "item_name": str,
            "date": str,
            "risk_score": float (0-100),
            "risk_level": { "level", "label", "color", "emoji" },
            "factors": {
                "temperature": { "score", "value", "weight" },
                "humidity":    { "score", "value", "weight" },
                "shelf_life":  { "score", "value", "weight" },
                "oversupply":  { "score", "value", "weight" },
            }
        }
    """
    session = SessionLocal()
    
    try:
        # Get item info
        item = session.query(Item).filter(Item.id == item_id).first()
        if not item:
            return {"error": f"Item {item_id} not found"}
        
        # Determine target date (default: latest date in weather data)
        if target_date is None:
            latest_weather = (
                session.query(Weather.date)
                .filter(Weather.region_id == region_id)
                .order_by(Weather.date.desc())
                .first()
            )
            target_date = latest_weather[0] if latest_weather else date.today()
        
        # Get weather for target date
        weather = (
            session.query(Weather)
            .filter(Weather.region_id == region_id, Weather.date == target_date)
            .first()
        )
        
        if weather:
            temp_max = weather.temp_max
            humidity = weather.humidity
        else:
            # Fallback: use reasonable defaults
            temp_max = 32.0
            humidity = 65.0
        
        # Get yesterday's sales volume (supply proxy)
        yesterday = target_date - timedelta(days=1)
        yesterday_sales = (
            session.query(SalesVolume.volume_kg)
            .filter(
                SalesVolume.item_id == item_id,
                SalesVolume.region_id == region_id,
                SalesVolume.date == yesterday,
            )
            .first()
        )
        yesterday_vol = yesterday_sales[0] if yesterday_sales else 0
        
        # If no forecasted demand provided, use 7-day average as proxy
        if forecasted_demand is None:
            week_ago = target_date - timedelta(days=7)
            week_sales = (
                session.query(SalesVolume.volume_kg)
                .filter(
                    SalesVolume.item_id == item_id,
                    SalesVolume.region_id == region_id,
                    SalesVolume.date >= week_ago,
                    SalesVolume.date < target_date,
                )
                .all()
            )
            forecasted_demand = (
                sum(s[0] for s in week_sales) / max(len(week_sales), 1)
                if week_sales else yesterday_vol
            )
        
        # ─── Compute individual factor scores ────────────────────────────
        temp_score = _temperature_score(temp_max)
        humid_score = _humidity_score(humidity)
        shelf_score = _shelf_life_score(item.shelf_life_days, days_since_harvest)
        oversupply_score = _oversupply_score(yesterday_vol, forecasted_demand)
        
        # ─── Weighted composite score ────────────────────────────────────
        risk_score = (
            temp_score * RISK_WEIGHT_TEMPERATURE +
            humid_score * RISK_WEIGHT_HUMIDITY +
            shelf_score * RISK_WEIGHT_SHELF_LIFE +
            oversupply_score * RISK_WEIGHT_OVERSUPPLY
        )
        risk_score = round(min(100, max(0, risk_score)), 1)
        
        return {
            "item_id": item_id,
            "region_id": region_id,
            "item_name": item.name,
            "date": target_date.isoformat(),
            "risk_score": risk_score,
            "risk_level": get_risk_level(risk_score),
            "factors": {
                "temperature": {
                    "score": round(temp_score, 1),
                    "value": f"{temp_max}°C",
                    "weight": RISK_WEIGHT_TEMPERATURE,
                },
                "humidity": {
                    "score": round(humid_score, 1),
                    "value": f"{humidity}%",
                    "weight": RISK_WEIGHT_HUMIDITY,
                },
                "shelf_life": {
                    "score": round(shelf_score, 1),
                    "value": f"{item.shelf_life_days} days (day {days_since_harvest})",
                    "weight": RISK_WEIGHT_SHELF_LIFE,
                },
                "oversupply": {
                    "score": round(oversupply_score, 1),
                    "value": f"supply={yesterday_vol:.0f}kg, demand={forecasted_demand:.0f}kg",
                    "weight": RISK_WEIGHT_OVERSUPPLY,
                },
            },
        }
    
    finally:
        session.close()
