"""
MandiSense Price Advisor — Rule-Based Recommendation Engine
============================================================
Takes forecast + spoilage risk output and produces structured
price adjustment recommendations with reason codes.

This is the CORE recommendation logic — it works entirely offline
without any LLM. The LLM layer (llm_service.py) wraps these
structured outputs into natural-language explanations.

Pricing Rules:
    1. High spoilage risk (>66)     → aggressive discount (-10% to -20%)
    2. Moderate spoilage risk (34-66)→ mild discount (-3% to -8%)
    3. Demand spike forecast        → price increase (+3% to +10%)
    4. Demand drop forecast         → mild discount (-3% to -5%)
    5. Oversupply signal            → discount (-5% to -10%)
    6. Weather disruption expected  → hold or raise price (+2% to +5%)

Multiple rules can apply — the final adjustment is a weighted blend.
"""

import sys
import os
from datetime import date, timedelta
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.database import SessionLocal
from app.db.models import Item, DailyPrice, Weather, SalesVolume
from app.forecasting.demand_forecast import forecast_demand
from app.forecasting.spoilage_risk import compute_spoilage_risk


# ═══════════════════════════════════════════════════════════════════════════════
# REASON CODES — structured, machine-readable labels for each recommendation
# ═══════════════════════════════════════════════════════════════════════════════

REASON_CODES = {
    "HIGH_SPOILAGE":       {"label": "High Spoilage Risk",      "icon": "🔴", "priority": 1},
    "MODERATE_SPOILAGE":   {"label": "Moderate Spoilage Risk",  "icon": "🟡", "priority": 2},
    "DEMAND_SPIKE":        {"label": "Demand Spike Expected",   "icon": "📈", "priority": 2},
    "DEMAND_DROP":         {"label": "Demand Drop Expected",    "icon": "📉", "priority": 3},
    "OVERSUPPLY":          {"label": "Oversupply Detected",     "icon": "📦", "priority": 2},
    "WEATHER_DISRUPTION":  {"label": "Weather Disruption",      "icon": "🌧️", "priority": 3},
    "STABLE":              {"label": "Market Stable",           "icon": "✅", "priority": 5},
}


def _get_demand_trend(forecasts: list, recent_avg: float) -> tuple:
    """
    Compare forecasted demand against recent average.
    Returns (trend_label, pct_change).
    
    trend: 'spike' | 'drop' | 'stable'
    """
    if not forecasts:
        return "stable", 0.0
    
    forecast_avg = sum(f["predicted_volume"] for f in forecasts) / len(forecasts)
    
    if recent_avg <= 0:
        return "stable", 0.0
    
    pct_change = (forecast_avg - recent_avg) / recent_avg * 100
    
    if pct_change > 10:
        return "spike", pct_change
    elif pct_change < -10:
        return "drop", pct_change
    else:
        return "stable", pct_change


def _get_weather_risk(region_id: int, target_date: date = None) -> tuple:
    """
    Check if weather conditions suggest supply disruption.
    Returns (is_disruption, details_str).
    """
    session = SessionLocal()
    try:
        if target_date is None:
            latest = (
                session.query(Weather.date)
                .filter(Weather.region_id == region_id)
                .order_by(Weather.date.desc())
                .first()
            )
            target_date = latest[0] if latest else date.today()
        
        weather = (
            session.query(Weather)
            .filter(Weather.region_id == region_id, Weather.date == target_date)
            .first()
        )
        
        if not weather:
            return False, ""
        
        # Heavy rain or extreme heat = disruption risk
        if weather.rainfall_mm > 30:
            return True, f"Heavy rainfall ({weather.rainfall_mm:.0f}mm)"
        if weather.temp_max > 42:
            return True, f"Extreme heat ({weather.temp_max:.0f}°C)"
        
        return False, ""
    finally:
        session.close()


def _get_recent_volume_avg(item_id: int, region_id: int, days: int = 7) -> float:
    """Get average sales volume over the last N days."""
    session = SessionLocal()
    try:
        latest = (
            session.query(SalesVolume.date)
            .filter(SalesVolume.item_id == item_id, SalesVolume.region_id == region_id)
            .order_by(SalesVolume.date.desc())
            .first()
        )
        if not latest:
            return 0.0
        
        cutoff = latest[0] - timedelta(days=days)
        records = (
            session.query(SalesVolume.volume_kg)
            .filter(
                SalesVolume.item_id == item_id,
                SalesVolume.region_id == region_id,
                SalesVolume.date > cutoff,
            )
            .all()
        )
        if not records:
            return 0.0
        return sum(r[0] for r in records) / len(records)
    finally:
        session.close()


def _get_current_price(item_id: int, region_id: int) -> float:
    """Get the most recent wholesale price."""
    session = SessionLocal()
    try:
        latest = (
            session.query(DailyPrice.wholesale_price)
            .filter(DailyPrice.item_id == item_id, DailyPrice.region_id == region_id)
            .order_by(DailyPrice.date.desc())
            .first()
        )
        return latest[0] if latest else 0.0
    finally:
        session.close()


def generate_recommendation(item_id: int, region_id: int) -> dict:
    """
    Generate a complete price recommendation for an item in a region.
    
    This is the main entry point for the recommendation engine.
    
    Returns:
        {
            "item_id": int,
            "region_id": int,
            "item_name": str,
            "current_price": float,
            "suggested_price": float,
            "price_change_pct": float,       # e.g., -8.0 means reduce by 8%
            "action": "reduce" | "increase" | "hold",
            "confidence": "high" | "medium" | "low",
            "reasons": [
                {
                    "code": str,
                    "label": str,
                    "icon": str,
                    "detail": str,
                    "impact_pct": float,
                }
            ],
            "risk_score": float,
            "risk_level": dict,
            "demand_forecast": list,
            "summary": str,                  # One-line structured summary
        }
    """
    # ─── Gather all inputs ────────────────────────────────────────────────
    
    # 1. Spoilage risk
    risk_data = compute_spoilage_risk(item_id, region_id)
    risk_score = risk_data.get("risk_score", 0)
    risk_level = risk_data.get("risk_level", {})
    item_name = risk_data.get("item_name", f"Item #{item_id}")
    
    # 2. Demand forecast
    forecast_data = forecast_demand(item_id, region_id)
    forecasts = forecast_data.get("forecasts", [])
    
    # 3. Recent demand average
    recent_avg = _get_recent_volume_avg(item_id, region_id)
    
    # 4. Demand trend
    demand_trend, demand_pct = _get_demand_trend(forecasts, recent_avg)
    
    # 5. Weather disruption
    weather_disruption, weather_detail = _get_weather_risk(region_id)
    
    # 6. Current price
    current_price = _get_current_price(item_id, region_id)
    
    # ─── Apply pricing rules ─────────────────────────────────────────────
    
    reasons = []
    total_adjustment = 0.0
    
    # Rule 1: Spoilage risk
    if risk_score > 66:
        adj = -15.0  # Aggressive discount
        reasons.append({
            "code": "HIGH_SPOILAGE",
            "label": REASON_CODES["HIGH_SPOILAGE"]["label"],
            "icon": REASON_CODES["HIGH_SPOILAGE"]["icon"],
            "detail": f"Spoilage risk at {risk_score:.0f}/100 — stock may go waste",
            "impact_pct": adj,
        })
        total_adjustment += adj
    elif risk_score > 33:
        adj = -5.0
        reasons.append({
            "code": "MODERATE_SPOILAGE",
            "label": REASON_CODES["MODERATE_SPOILAGE"]["label"],
            "icon": REASON_CODES["MODERATE_SPOILAGE"]["icon"],
            "detail": f"Spoilage risk at {risk_score:.0f}/100 — sell faster to avoid waste",
            "impact_pct": adj,
        })
        total_adjustment += adj
    
    # Rule 2: Demand trend
    if demand_trend == "spike":
        adj = min(10.0, demand_pct * 0.3)  # Cap at +10%
        reasons.append({
            "code": "DEMAND_SPIKE",
            "label": REASON_CODES["DEMAND_SPIKE"]["label"],
            "icon": REASON_CODES["DEMAND_SPIKE"]["icon"],
            "detail": f"Demand expected to rise {demand_pct:.0f}% over next 3 days",
            "impact_pct": adj,
        })
        total_adjustment += adj
    elif demand_trend == "drop":
        adj = max(-8.0, demand_pct * 0.3)  # Cap at -8%
        reasons.append({
            "code": "DEMAND_DROP",
            "label": REASON_CODES["DEMAND_DROP"]["label"],
            "icon": REASON_CODES["DEMAND_DROP"]["icon"],
            "detail": f"Demand expected to fall {abs(demand_pct):.0f}% over next 3 days",
            "impact_pct": adj,
        })
        total_adjustment += adj
    
    # Rule 3: Weather disruption
    if weather_disruption:
        adj = 3.0  # Supply squeeze → can raise price
        reasons.append({
            "code": "WEATHER_DISRUPTION",
            "label": REASON_CODES["WEATHER_DISRUPTION"]["label"],
            "icon": REASON_CODES["WEATHER_DISRUPTION"]["icon"],
            "detail": weather_detail,
            "impact_pct": adj,
        })
        total_adjustment += adj
    
    # If no signals → market stable
    if not reasons:
        reasons.append({
            "code": "STABLE",
            "label": REASON_CODES["STABLE"]["label"],
            "icon": REASON_CODES["STABLE"]["icon"],
            "detail": "No significant risk or demand shifts detected",
            "impact_pct": 0.0,
        })
    
    # ─── Compute final price ─────────────────────────────────────────────
    
    # Clamp adjustment to [-20%, +15%] range
    total_adjustment = max(-20.0, min(15.0, total_adjustment))
    total_adjustment = round(total_adjustment, 1)
    
    suggested_price = round(current_price * (1 + total_adjustment / 100) * 2) / 2  # Round to ₹0.5
    suggested_price = max(suggested_price, 1.0)  # Floor at ₹1
    
    # Action label
    if total_adjustment < -1:
        action = "reduce"
    elif total_adjustment > 1:
        action = "increase"
    else:
        action = "hold"
    
    # Confidence based on data quality
    if len(forecasts) >= 3 and risk_score > 0:
        confidence = "high"
    elif len(forecasts) > 0:
        confidence = "medium"
    else:
        confidence = "low"
    
    # One-line summary
    if action == "reduce":
        summary = f"Reduce {item_name} price by {abs(total_adjustment):.0f}% to Rs.{suggested_price:.0f}/kg"
    elif action == "increase":
        summary = f"Increase {item_name} price by {total_adjustment:.0f}% to Rs.{suggested_price:.0f}/kg"
    else:
        summary = f"Hold {item_name} at current price Rs.{current_price:.0f}/kg"
    
    # Sort reasons by priority
    reasons.sort(key=lambda r: REASON_CODES.get(r["code"], {}).get("priority", 99))
    
    return {
        "item_id": item_id,
        "region_id": region_id,
        "item_name": item_name,
        "current_price": current_price,
        "suggested_price": suggested_price,
        "price_change_pct": total_adjustment,
        "action": action,
        "confidence": confidence,
        "reasons": reasons,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "demand_forecast": forecasts,
        "summary": summary,
    }


def generate_all_recommendations(region_id: int) -> list:
    """
    Generate recommendations for ALL items in a region.
    This powers the "Today" dashboard view.
    """
    session = SessionLocal()
    try:
        items = session.query(Item).all()
        results = []
        for item in items:
            rec = generate_recommendation(item.id, region_id)
            results.append(rec)
        return results
    finally:
        session.close()
