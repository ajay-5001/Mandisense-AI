"""
MandiSense API Routes
======================
All FastAPI endpoints for the MandiSense application.

Endpoints:
    GET  /api/items                          — List all items
    GET  /api/regions                        — List all regions
    GET  /api/items/{item_id}/prices         — Price history for an item
    GET  /api/regions/{region_id}/weather     — Weather data for a region
    GET  /api/forecast/{item_id}/{region_id}  — Demand forecast
    GET  /api/risk/{item_id}/{region_id}      — Spoilage risk score
    GET  /api/recommend/{item_id}/{region_id} — Full recommendation
    GET  /api/recommend/all/{region_id}       — All items for a region (dashboard)
    GET  /api/trends/{item_id}/{region_id}    — Historical trends for charts
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, Query, HTTPException, Header
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random

from app.db.database import SessionLocal
from app.db.models import Item, Region, DailyPrice, Weather, SalesVolume, VendorProduct, PurchasePlan
from app.forecasting.demand_forecast import forecast_demand
from app.forecasting.spoilage_risk import compute_spoilage_risk
from app.recommendation.price_advisor import generate_recommendation, generate_all_recommendations
from app.recommendation.llm_service import generate_explanation, generate_explanation_llm
from app.recommendation.gemini_service import (
    generate_explanation_gemini,
    generate_daily_summary_gemini,
    generate_chat_response_gemini
)

def get_mock_stock(item_id: int, region_id: int) -> float:
    """Deterministic mock stock based on item_id and region_id."""
    rng = random.Random(item_id * 100 + region_id)
    return round(rng.uniform(25.0, 95.0), 1)

class ChatRequest(BaseModel):
    query: str
    region_id: int
    language: str = "en"
    history: List[Dict[str, str]] = []

router = APIRouter(prefix="/api", tags=["MandiSense API"])


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER DATA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/items")
def list_items():
    """Get all 15 perishable items."""
    session = SessionLocal()
    try:
        items = session.query(Item).all()
        return [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "base_price": item.base_price,
                "shelf_life_days": item.shelf_life_days,
                "unit": item.unit,
            }
            for item in items
        ]
    finally:
        session.close()


@router.get("/regions")
def list_regions():
    """Get all 3 market regions."""
    session = SessionLocal()
    try:
        regions = session.query(Region).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "state": r.state,
                "latitude": r.latitude,
                "longitude": r.longitude,
            }
            for r in regions
        ]
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PRICE & WEATHER DATA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/items/{item_id}/prices")
def get_price_history(
    item_id: int,
    region_id: int = Query(1, description="Region ID"),
    days: int = Query(30, description="Number of days of history"),
):
    """Get price history for an item in a region."""
    session = SessionLocal()
    try:
        records = (
            session.query(DailyPrice)
            .filter(DailyPrice.item_id == item_id, DailyPrice.region_id == region_id)
            .order_by(DailyPrice.date.desc())
            .limit(days)
            .all()
        )
        if not records:
            raise HTTPException(status_code=404, detail="No price data found")
        
        return [
            {
                "date": r.date.isoformat(),
                "wholesale_price": r.wholesale_price,
                "retail_price": r.retail_price,
            }
            for r in reversed(records)
        ]
    finally:
        session.close()


@router.get("/regions/{region_id}/weather")
def get_weather(
    region_id: int,
    days: int = Query(7, description="Number of days of history"),
):
    """Get weather data for a region."""
    session = SessionLocal()
    try:
        records = (
            session.query(Weather)
            .filter(Weather.region_id == region_id)
            .order_by(Weather.date.desc())
            .limit(days)
            .all()
        )
        if not records:
            raise HTTPException(status_code=404, detail="No weather data found")
        
        return [
            {
                "date": r.date.isoformat(),
                "temp_max": r.temp_max,
                "temp_min": r.temp_min,
                "humidity": r.humidity,
                "rainfall_mm": r.rainfall_mm,
            }
            for r in reversed(records)
        ]
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FORECASTING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/forecast/{item_id}/{region_id}")
def get_forecast(item_id: int, region_id: int):
    """Get 3-day demand forecast for an item in a region."""
    result = forecast_demand(item_id, region_id)
    if not result.get("forecasts"):
        raise HTTPException(status_code=404, detail="Insufficient data for forecast")
    return result


@router.get("/risk/{item_id}/{region_id}")
def get_spoilage_risk(item_id: int, region_id: int):
    """Get spoilage risk score for an item in a region."""
    result = compute_spoilage_risk(item_id, region_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/recommend/all/{region_id}")
def get_all_recommendations(
    region_id: int,
    lang: str = Query("en", description="Language: en, hi, or ta"),
):
    """
    Get pricing recommendations for ALL custom items in the vendor catalog.
    Powers the main dashboard "Today" view.
    """
    session = SessionLocal()
    try:
        vendor_prods = session.query(VendorProduct).all()
        recommendations = []
        
        for vp in vendor_prods:
            item = session.query(Item).filter(Item.name.ilike(vp.name)).first()
            if item:
                # Retrieve base pricing recommendations
                rec = generate_recommendation(item.id, region_id)
                # Override prices/stocks with user catalog values
                rec["current_price"] = vp.purchase_price
                ratio = vp.purchase_price / max(item.base_price, 1.0)
                rec["suggested_price"] = round(rec.get("suggested_price", vp.selling_price) * ratio, 2)
                rec["price_change_pct"] = round(((rec["suggested_price"] - vp.selling_price) / max(vp.selling_price, 1.0)) * 100, 1)
                rec["stock_kg"] = vp.current_stock
                if rec["price_change_pct"] < -1:
                    rec["action"] = "reduce"
                elif rec["price_change_pct"] > 1:
                    rec["action"] = "increase"
                else:
                    rec["action"] = "hold"
            else:
                # Custom item (Rice, Flowers, Spices, etc.) - Simulate base values
                weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(Weather.date.desc()).first()
                temp = weather.temp_max if weather else 30.0
                humidity = weather.humidity if weather else 50.0
                rain = weather.rainfall_mm if weather else 0.0
                
                base_shelf = 10 if vp.category.lower() in ["grain", "spice"] else 4
                risk_score = min(95.0, max(15.0, (temp * 0.8 + humidity * 0.4) * (5.0 / base_shelf)))
                
                demand_factor = 1.0
                if rain > 5.0:
                    demand_factor -= 0.15
                if temp > 35.0 and vp.category.lower() not in ["grain", "spice"]:
                    demand_factor -= 0.10
                    
                suggested_price = round(vp.selling_price * (1.0 + (demand_factor - 1.0) * 0.5), 2)
                price_change_pct = round(((suggested_price - vp.selling_price) / max(vp.selling_price, 1.0)) * 100, 1)
                
                forecasts = [
                    {"date": (date.today() + timedelta(days=d)).isoformat(), "predicted_volume": round(vp.current_stock * 0.25 * demand_factor, 1)}
                    for d in range(1, 4)
                ]
                
                if price_change_pct < -1:
                    action = "reduce"
                elif price_change_pct > 1:
                    action = "increase"
                else:
                    action = "hold"
                    
                reasons = []
                if risk_score > 66:
                    reasons.append({
                        "code": "HIGH_SPOILAGE",
                        "label": "High Spoilage Risk",
                        "icon": "🔴",
                        "detail": f"Spoilage risk at {risk_score:.0f}/100",
                        "impact_pct": -15.0
                    })
                elif risk_score > 33:
                    reasons.append({
                        "code": "MODERATE_SPOILAGE",
                        "label": "Moderate Spoilage Risk",
                        "icon": "🟡",
                        "detail": f"Spoilage risk at {risk_score:.0f}/100",
                        "impact_pct": -5.0
                    })
                
                if rain > 5.0:
                    reasons.append({
                        "code": "WEATHER_DISRUPTION",
                        "label": "Weather Disruption",
                        "icon": "🌧️",
                        "detail": f"Heavy rainfall ({rain:.0f}mm)",
                        "impact_pct": -15.0
                    })
                
                if not reasons:
                    reasons.append({
                        "code": "STABLE",
                        "label": "Market Stable",
                        "icon": "✅",
                        "detail": "No significant risk or demand shifts detected",
                        "impact_pct": 0.0
                    })
                
                rec = {
                    "item_id": vp.id + 1000,
                    "item_name": vp.name,
                    "category": vp.category,
                    "current_price": vp.purchase_price,
                    "suggested_price": suggested_price,
                    "price_change_pct": price_change_pct,
                    "action": action,
                    "reasons": reasons,
                    "risk_score": risk_score,
                    "risk_level": {"level": "high" if risk_score > 66 else "moderate" if risk_score > 33 else "low"},
                    "explanation": f"Custom recommendations for {vp.name} aligned with weather parameters.",
                    "demand_forecast": forecasts,
                    "stock_kg": vp.current_stock
                }
                
            rec["explanation"] = generate_explanation(rec, lang)
            rec["language"] = lang
            recommendations.append(rec)
            
        recommendations.sort(key=lambda r: r.get("risk_score", 0), reverse=True)
        
        return {
            "region_id": region_id,
            "date": date.today().isoformat(),
            "language": lang,
            "total_items": len(recommendations),
            "recommendations": recommendations,
        }
    finally:
        session.close()


@router.get("/recommend/{item_id}/{region_id}")
async def get_recommendation(
    item_id: int,
    region_id: int,
    lang: str = Query("en", description="Language: en, hi, or ta"),
    use_llm: bool = Query(False, description="Use LLM for explanation (requires API key)"),
    x_gemini_key: Optional[str] = Header(None),
):
    """
    Get full pricing recommendation details for a specific item.
    """
    session = SessionLocal()
    try:
        if item_id >= 1000:
            vp_id = item_id - 1000
            vp = session.query(VendorProduct).filter(VendorProduct.id == vp_id).first()
            if not vp:
                raise HTTPException(status_code=404, detail="Custom product not found")
                
            weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(Weather.date.desc()).first()
            temp = weather.temp_max if weather else 30.0
            humidity = weather.humidity if weather else 50.0
            rain = weather.rainfall_mm if weather else 0.0
            
            base_shelf = 10 if vp.category.lower() in ["grain", "spice"] else 4
            risk_score = min(95.0, max(15.0, (temp * 0.8 + humidity * 0.4) * (5.0 / base_shelf)))
            
            demand_factor = 1.0
            if rain > 5.0:
                demand_factor -= 0.15
            if temp > 35.0 and vp.category.lower() not in ["grain", "spice"]:
                demand_factor -= 0.10
                
            suggested_price = round(vp.selling_price * (1.0 + (demand_factor - 1.0) * 0.5), 2)
            price_change_pct = round(((suggested_price - vp.selling_price) / max(vp.selling_price, 1.0)) * 100, 1)
            
            forecasts = [
                {"date": (date.today() + timedelta(days=d)).isoformat(), "predicted_volume": round(vp.current_stock * 0.25 * demand_factor, 1)}
                for d in range(1, 4)
            ]
            
            if price_change_pct < -1:
                action = "reduce"
            elif price_change_pct > 1:
                action = "increase"
            else:
                action = "hold"
                
            reasons = []
            if risk_score > 66:
                reasons.append({
                    "code": "HIGH_SPOILAGE",
                    "label": "High Spoilage Risk",
                    "icon": "🔴",
                    "detail": f"Spoilage risk at {risk_score:.0f}/100",
                    "impact_pct": -15.0
                })
            elif risk_score > 33:
                reasons.append({
                    "code": "MODERATE_SPOILAGE",
                    "label": "Moderate Spoilage Risk",
                    "icon": "🟡",
                    "detail": f"Spoilage risk at {risk_score:.0f}/100",
                    "impact_pct": -5.0
                })
            
            if rain > 5.0:
                reasons.append({
                    "code": "WEATHER_DISRUPTION",
                    "label": "Weather Disruption",
                    "icon": "🌧️",
                    "detail": f"Heavy rainfall ({rain:.0f}mm)",
                    "impact_pct": -15.0
                })
            
            if not reasons:
                reasons.append({
                    "code": "STABLE",
                    "label": "Market Stable",
                    "icon": "✅",
                    "detail": "No significant risk or demand shifts detected",
                    "impact_pct": 0.0
                })
            
            rec = {
                "item_id": item_id,
                "item_name": vp.name,
                "category": vp.category,
                "current_price": vp.purchase_price,
                "suggested_price": suggested_price,
                "price_change_pct": price_change_pct,
                "action": action,
                "reasons": reasons,
                "risk_score": risk_score,
                "risk_level": {"level": "high" if risk_score > 66 else "moderate" if risk_score > 33 else "low"},
                "explanation": f"Optimized suggestions for {vp.name}.",
                "demand_forecast": forecasts,
                "stock_kg": vp.current_stock,
                "temperature": temp,
                "humidity": humidity
            }
        else:
            item = session.query(Item).filter(Item.id == item_id).first()
            vp = session.query(VendorProduct).filter(VendorProduct.name.ilike(item.name)).first() if item else None
            
            rec = generate_recommendation(item_id, region_id)
            latest_weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(Weather.date.desc()).first()
            rec["temperature"] = latest_weather.temp_max if latest_weather else 30.0
            rec["humidity"] = latest_weather.humidity if latest_weather else 60.0
            
            if vp:
                rec["current_price"] = vp.purchase_price
                ratio = vp.purchase_price / max(item.base_price, 1.0)
                rec["suggested_price"] = round(rec.get("suggested_price", vp.selling_price) * ratio, 2)
                rec["price_change_pct"] = round(((rec["suggested_price"] - vp.selling_price) / max(vp.selling_price, 1.0)) * 100, 1)
                rec["stock_kg"] = vp.current_stock
                if rec["price_change_pct"] < -1:
                    rec["action"] = "reduce"
                elif rec["price_change_pct"] > 1:
                    rec["action"] = "increase"
                else:
                    rec["action"] = "hold"
            else:
                rec["stock_kg"] = get_mock_stock(item_id, region_id)
                
            rec["forecast_demand_today"] = rec["demand_forecast"][0]["predicted_volume"] if rec.get("demand_forecast") else 0.0
            
        key = x_gemini_key or os.getenv("GEMINI_API_KEY", "")
        if key:
            try:
                gemini_result = await generate_explanation_gemini(rec, lang, key)
                rec["gemini_details"] = gemini_result
                rec["explanation"] = gemini_result.get("business_explanation", rec.get("explanation", ""))
                rec["gemini_active"] = True
            except Exception as e:
                print(f"Failed to generate Gemini explanation: {e}")
                rec["explanation"] = generate_explanation(rec, lang)
                rec["gemini_active"] = False
        else:
            if use_llm:
                rec["explanation"] = await generate_explanation_llm(rec, lang)
            else:
                rec["explanation"] = generate_explanation(rec, lang)
            rec["gemini_active"] = False
            
        rec["language"] = lang
        return rec
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════════════════
# TRENDS ENDPOINT (for charts)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/trends/{item_id}/{region_id}")
def get_trends(
    item_id: int,
    region_id: int,
    days: int = Query(30, description="Number of days of history"),
):
    """
    Get combined price + volume trends for chart rendering.
    """
    session = SessionLocal()
    try:
        if item_id >= 1000:
            vp_id = item_id - 1000
            vp = session.query(VendorProduct).filter(VendorProduct.id == vp_id).first()
            if not vp:
                raise HTTPException(status_code=404, detail="Custom product not found")
                
            rng = random.Random(vp_id * 100 + region_id)
            dates = [date.today() - timedelta(days=d) for d in range(days)]
            dates.reverse()
            
            prices_list = []
            volumes_list = []
            weather_list = []
            
            weather_records = (
                session.query(Weather)
                .filter(Weather.region_id == region_id)
                .order_by(Weather.date.desc())
                .limit(days)
                .all()
            )
            weather_records.reverse()
            
            for d_idx, d in enumerate(dates):
                var = 1.0 + (rng.uniform(-0.08, 0.08))
                w_p = round(vp.purchase_price * var, 2)
                r_p = round(vp.selling_price * var, 2)
                vol = round(vp.current_stock * 0.2 * var, 1)
                
                prices_list.append({"date": d.isoformat(), "wholesale": w_p, "retail": r_p})
                volumes_list.append({"date": d.isoformat(), "volume_kg": vol, "footfall": int(vol / 1.5)})
                
                if d_idx < len(weather_records):
                    w_rec = weather_records[d_idx]
                    weather_list.append({"date": d.isoformat(), "temp_max": w_rec.temp_max, "humidity": w_rec.humidity, "rainfall": w_rec.rainfall_mm})
                else:
                    weather_list.append({"date": d.isoformat(), "temp_max": 30.0, "humidity": 60.0, "rainfall": 0.0})
                    
            forecasts = [
                {"date": (date.today() + timedelta(days=d)).isoformat(), "predicted_volume": round(vp.current_stock * 0.2, 1), "confidence_lower": round(vp.current_stock * 0.15, 1), "confidence_upper": round(vp.current_stock * 0.25, 1)}
                for d in range(1, 4)
            ]
            
            return {
                "item_id": item_id,
                "item_name": vp.name,
                "region_id": region_id,
                "days": days,
                "prices": prices_list,
                "volumes": volumes_list,
                "weather": weather_list,
                "forecasts": forecasts
            }
            
        item = session.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        prices = (
            session.query(DailyPrice.date, DailyPrice.wholesale_price, DailyPrice.retail_price)
            .filter(DailyPrice.item_id == item_id, DailyPrice.region_id == region_id)
            .order_by(DailyPrice.date.desc())
            .limit(days)
            .all()
        )
        
        volumes = (
            session.query(SalesVolume.date, SalesVolume.volume_kg, SalesVolume.footfall)
            .filter(SalesVolume.item_id == item_id, SalesVolume.region_id == region_id)
            .order_by(SalesVolume.date.desc())
            .limit(days)
            .all()
        )
        
        weather = (
            session.query(Weather.date, Weather.temp_max, Weather.humidity, Weather.rainfall_mm)
            .filter(Weather.region_id == region_id)
            .order_by(Weather.date.desc())
            .limit(days)
            .all()
        )
        
        fc_data = forecast_demand(item_id, region_id)
        forecasts = fc_data.get("forecasts", [])
        
        return {
            "item_id": item_id,
            "item_name": item.name,
            "region_id": region_id,
            "days": days,
            "prices": [{"date": p[0].isoformat(), "wholesale": p[1], "retail": p[2]} for p in reversed(prices)],
            "volumes": [{"date": v[0].isoformat(), "volume_kg": v[1], "footfall": v[2]} for v in reversed(volumes)],
            "weather": [{"date": w[0].isoformat(), "temp_max": w[1], "humidity": w[2], "rainfall": w[3]} for w in reversed(weather)],
            "forecasts": forecasts
        }
    finally:
        session.close()


@router.get("/inventory/{region_id}")
def get_inventory(
    region_id: int,
    lang: str = Query("en", description="Language: en, hi, or ta"),
):
    """Get detailed inventory analysis for all custom products in the vendor catalog."""
    session = SessionLocal()
    try:
        vendor_prods = session.query(VendorProduct).all()
        results = []
        for vp in vendor_prods:
            item = session.query(Item).filter(Item.name.ilike(vp.name)).first()
            item_id = item.id if item else (vp.id + 1000)
            
            if item:
                rec = generate_recommendation(item.id, region_id)
                forecasts = rec.get("demand_forecast", [])
                expected_demand = forecasts[0]["predicted_volume"] if forecasts else 15.0
                spoilage_risk = rec.get("risk_score", 0)
                mandi_price = rec.get("current_price", item.base_price)
            else:
                weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(Weather.date.desc()).first()
                temp = weather.temp_max if weather else 30.0
                humidity = weather.humidity if weather else 50.0
                
                base_shelf = 10 if vp.category.lower() in ["grain", "spice"] else 4
                spoilage_risk = min(95.0, max(15.0, (temp * 0.8 + humidity * 0.4) * (5.0 / base_shelf)))
                expected_demand = round(vp.current_stock * 0.25, 1)
                mandi_price = vp.purchase_price
                forecasts = [
                    {"date": (date.today() + timedelta(days=d)).isoformat(), "predicted_volume": round(vp.current_stock * 0.25, 1)}
                    for d in range(1, 4)
                ]
                
            stock = vp.current_stock
            days_remaining = round(stock / max(expected_demand, 1.0), 1)
            low_stock = stock < (expected_demand * 1.5)
            
            plan = session.query(PurchasePlan).filter(PurchasePlan.product_name.ilike(vp.name)).first()
            planned_qty = plan.planned_qty if plan else 0.0
            
            total_3d_demand = sum(f["predicted_volume"] for f in forecasts) if forecasts else expected_demand * 3
            ideal_buy = max(5.0, round(total_3d_demand - stock, 1))
            
            if planned_qty > 0:
                if planned_qty > ideal_buy * 1.3:
                    ai_purchase = f"Overstock Risk: Planned {planned_qty} {vp.unit}, but recommended buy is {ideal_buy} {vp.unit} due to demand constraints."
                elif planned_qty < ideal_buy * 0.7:
                    ai_purchase = f"Understock Risk: Planned {planned_qty} {vp.unit}, but recommend buying {ideal_buy} {vp.unit} to meet demand."
                else:
                    ai_purchase = f"Optimal Procurement Plan: Buy {planned_qty} {vp.unit} is well-aligned with demand forecasts."
            else:
                if low_stock:
                    ai_purchase = f"Buy {ideal_buy} {vp.unit} to cover 3-day demand forecast."
                elif spoilage_risk > 66:
                    ai_purchase = "Hold purchases. Spoilage risk is extremely high today."
                else:
                    ai_purchase = f"Adequate stock ({stock} {vp.unit}). No immediate restock needed."
                    
            results.append({
                "item_id": item_id,
                "item_name": vp.name,
                "category": vp.category,
                "stock": stock,
                "unit": vp.unit,
                "spoilage_risk": spoilage_risk,
                "expected_demand": expected_demand,
                "mandi_price": mandi_price,
                "selling_price": vp.selling_price,
                "recommended_selling_price": vp.selling_price,
                "days_remaining": days_remaining,
                "low_stock_warning": low_stock,
                "ai_purchase_suggestion": ai_purchase,
                "planned_purchase": planned_qty,
                "recommended_purchase": ideal_buy
            })
            
        return results
    finally:
        session.close()


@router.get("/ai-summary/{region_id}")
async def get_ai_summary(
    region_id: int,
    lang: str = Query("en", description="Language: en, hi, or ta"),
    x_gemini_key: Optional[str] = Header(None),
):
    """Get consolidated daily business summary widget from Gemini."""
    session = SessionLocal()
    try:
        region = session.query(Region).filter(Region.id == region_id).first()
        region_name = region.name if region else "Local Market"
        
        weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(Weather.date.desc()).first()
        recs = get_all_recommendations(region_id, lang)["recommendations"]
        
        total_items = len(recs)
        high_risk_items = [r["item_name"] for r in recs if r.get("risk_score", 0) > 66]
        discount_items = [r["item_name"] for r in recs if r.get("price_change_pct", 0) < 0]
        
        total_forecast_demand = sum(r["demand_forecast"][0]["predicted_volume"] for r in recs if r.get("demand_forecast"))
        
        estimated_profit = 0.0
        estimated_revenue = 0.0
        for r in recs:
            dem = r["demand_forecast"][0]["predicted_volume"] if r.get("demand_forecast") else 20.0
            sell_price = r["suggested_price"]
            cost_price = r["current_price"]
            estimated_revenue += dem * sell_price
            estimated_profit += dem * (sell_price - cost_price)
            
        summary_data = {
            "market": region_name,
            "date": date.today().isoformat(),
            "weather": {
                "temp_max": weather.temp_max if weather else 32.0,
                "humidity": weather.humidity if weather else 65.0,
                "rainfall_mm": weather.rainfall_mm if weather else 0.0
            },
            "total_items": total_items,
            "total_forecast_demand_kg": round(total_forecast_demand, 1),
            "estimated_revenue_inr": round(estimated_revenue, 1),
            "estimated_profit_inr": round(estimated_profit, 1),
            "high_risk_products": high_risk_items,
            "discount_products": discount_items,
            "low_stock_products": [
                r["item_name"] for r in recs 
                if r.get("stock_kg", 0.0) < (r["demand_forecast"][0]["predicted_volume"] if r.get("demand_forecast") else 20.0) * 1.5
            ]
        }
        
        key = x_gemini_key or os.getenv("GEMINI_API_KEY", "")
        if key:
            try:
                summary = await generate_daily_summary_gemini(summary_data, lang, key)
                return {
                    "summary": summary,
                    "gemini_active": True,
                    "raw_data": summary_data
                }
            except Exception as e:
                print(f"Failed to generate Gemini summary: {e}")
                
        fallback_summaries = {
            "en": {
                "overall_performance": f"Today's market conditions in {region_name} are normal. Spoilage risk is high for {len(high_risk_items)} items.",
                "expected_demand": f"Total expected sales volume across all items is {summary_data['total_forecast_demand_kg']} kg.",
                "high_risk_products": f"The following products are at risk: {', '.join(high_risk_items) if high_risk_items else 'None'}.",
                "suggested_discounts": f"Discounts are recommended on {', '.join(discount_items) if discount_items else 'None'}.",
                "weather_impact": f"Humidity is at {summary_data['weather']['humidity']}%. Rainfall is {summary_data['weather']['rainfall_mm']}mm.",
                "stock_warnings": f"Stock is running low for {len(summary_data['low_stock_products'])} products."
            },
            "hi": {
                "overall_performance": f"{region_name} में आज बाजार की स्थिति सामान्य है। {len(high_risk_items)} वस्तुओं के लिए खराब होने का खतरा अधिक है.",
                "expected_demand": f"सभी वस्तुओं में कुल अपेक्षित बिक्री मात्रा {summary_data['total_forecast_demand_kg']} किलोग्राम है.",
                "high_risk_products": f"निम्नलिखित उत्पाद जोखिम में हैं: {', '.join(high_risk_items) if high_risk_items else 'कोई नहीं'}.",
                "suggested_discounts": f"इन उत्पादों पर छूट की सिफारिश की जाती है: {', '.join(discount_items) if discount_items else 'कोई नहीं'}.",
                "weather_impact": f"आर्द्रता {summary_data['weather']['humidity']}% पर है। वर्षा {summary_data['weather']['rainfall_mm']} मिलीमीटर है.",
                "stock_warnings": f"{len(summary_data['low_stock_products'])} उत्पादों के लिए स्टॉक कम चल रहा है।"
            },
            "ta": {
                "overall_performance": f"{region_name} இல் இன்றைய சந்தை நிலவரம் சாதாரணமானது. {len(high_risk_items)} பொருட்களுக்கு கெட்டுப்போகும் ஆபத்து அதிகம்.",
                "expected_demand": f"அனைத்து பொருட்களின் மொத்த விற்பனை அளவு {summary_data['total_forecast_demand_kg']} கிலோ ஆகும்.",
                "high_risk_products": f"பின்வரும் தயாரிப்புகள் ஆபத்தில் உள்ளன: {', '.join(high_risk_items) if high_risk_items else 'ஏதுமில்லை'}.",
                "suggested_discounts": f"இவற்றில் தள்ளுபடிகள் பரிந்துரைக்கப்படுகின்றன: {', '.join(discount_items) if discount_items else 'ஏதுமில்லை'}.",
                "weather_impact": f"ஈரப்பதம் {summary_data['weather']['humidity']}% ஆக உள்ளது. மழைப்பொழிவு {summary_data['weather']['rainfall_mm']} மிமீ ஆகும்.",
                "stock_warnings": f"{len(summary_data['low_stock_products'])} தயாரிப்புகளுக்கான இருப்பு குறைவாக உள்ளது."
            }
        }
        return {
            "summary": fallback_summaries.get(lang, fallback_summaries["en"]),
            "gemini_active": False,
            "raw_data": summary_data
        }
    finally:
        session.close()


@router.post("/chat")
async def chat_assistant(
    request: ChatRequest,
    x_gemini_key: Optional[str] = Header(None),
):
    """Chat assistant endpoints with contextual injection."""
    session = SessionLocal()
    try:
        region_id = request.region_id
        region = session.query(Region).filter(Region.id == region_id).first()
        region_name = region.name if region else "Local Market"
        
        recs = get_all_recommendations(region_id, request.language)["recommendations"]
        weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(Weather.date.desc()).first()
        
        item_context = []
        for r in recs:
            item_context.append({
                "name": r["item_name"],
                "mandi_price": r["current_price"],
                "suggested_price": r["suggested_price"],
                "change_pct": r["price_change_pct"],
                "risk_score": r["risk_score"],
                "forecast_demand_today": r["demand_forecast"][0]["predicted_volume"] if r.get("demand_forecast") else 0,
                "stock": get_mock_stock(r["item_id"], region_id)
            })
            
        data_context = {
            "date": date.today().isoformat(),
            "weather": {
                "temp": weather.temp_max if weather else 30.0,
                "humidity": weather.humidity if weather else 65.0,
                "rainfall": weather.rainfall_mm if weather else 0.0
            },
            "products": item_context
        }
        
        key = x_gemini_key or os.getenv("GEMINI_API_KEY", "")
        if not key:
            query_lower = request.query.lower()
            response = ""
            
            if "tomato" in query_lower:
                tom_rec = next((x for x in item_context if x["name"].lower() == "tomato"), None)
                if tom_rec:
                    response = f"Tomato price is recommended at ₹{tom_rec['suggested_price']}/kg (wholesale ₹{tom_rec['mandi_price']}/kg). Spoilage risk is {tom_rec['risk_score']:.0f}/100 and stock is {tom_rec['stock']:.1f}kg. Please setup your Gemini API Key in Settings to unlock deep AI explanations!"
                else:
                    response = "Tomato data is not loaded."
            elif "buy" in query_lower or "purchase" in query_lower:
                low_stock_items = [x["name"] for x in item_context if x["stock"] < x["forecast_demand_today"] * 1.5]
                response = f"You should restock these items soon: {', '.join(low_stock_items[:3]) if low_stock_items else 'None'}. Provide a Gemini API key to get full purchase optimization details."
            elif "spoilage" in query_lower or "risk" in query_lower:
                high_risk = sorted(item_context, key=lambda x: x["risk_score"], reverse=True)[:3]
                high_risk_strs = [f"{x['name']} ({x['risk_score']:.0f}/100)" for x in high_risk]
                response = f"Highest spoilage risk items: {', '.join(high_risk_strs)}. Reduce their prices to sell faster."
            else:
                response = "Welcome to MandiSense! I can help you price your stock, optimize purchases, and analyze weather impacts. Please configure your Google Gemini API Key in the Settings tab to start chatting in real-time."
                
            return {"response": response}
            
        response_text = await generate_chat_response_gemini(
            query=request.query,
            region_name=region_name,
            history=request.history,
            language=request.language,
            data_context=data_context,
            api_key=key
        )
        
        return {"response": response_text}
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT CRUD & PURCHASE PLAN & COMPARE APIS (NEW)
# ═══════════════════════════════════════════════════════════════════════════════

class ProductCreate(BaseModel):
    name: str
    category: str
    unit: str = "kg"
    purchase_price: float
    selling_price: float
    current_stock: float = 0.0
    supplier_name: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    current_stock: Optional[float] = None
    supplier_name: Optional[str] = None

class PurchasePlanSave(BaseModel):
    product_name: str
    planned_qty: float

@router.get("/products")
def get_products():
    session = SessionLocal()
    try:
        products = session.query(VendorProduct).all()
        return products
    finally:
        session.close()

@router.post("/products")
def create_product(product: ProductCreate):
    session = SessionLocal()
    try:
        new_prod = VendorProduct(
            name=product.name,
            category=product.category,
            unit=product.unit,
            purchase_price=product.purchase_price,
            selling_price=product.selling_price,
            current_stock=product.current_stock,
            supplier_name=product.supplier_name
        )
        session.add(new_prod)
        session.commit()
        session.refresh(new_prod)
        return new_prod
    finally:
        session.close()

@router.put("/products/{id}")
def update_product(id: int, product: ProductUpdate):
    session = SessionLocal()
    try:
        db_prod = session.query(VendorProduct).filter(VendorProduct.id == id).first()
        if not db_prod:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_prod, key, value)
        session.commit()
        session.refresh(db_prod)
        return db_prod
    finally:
        session.close()

@router.delete("/products/{id}")
def delete_product(id: int):
    session = SessionLocal()
    try:
        db_prod = session.query(VendorProduct).filter(VendorProduct.id == id).first()
        if not db_prod:
            raise HTTPException(status_code=404, detail="Product not found")
        session.delete(db_prod)
        session.commit()
        return {"status": "success", "message": f"Product {id} deleted"}
    finally:
        session.close()

@router.get("/purchase-plans")
def get_purchase_plans():
    session = SessionLocal()
    try:
        plans = session.query(PurchasePlan).all()
        return plans
    finally:
        session.close()

@router.post("/purchase-plans")
def save_purchase_plans(plans: List[PurchasePlanSave]):
    session = SessionLocal()
    try:
        session.query(PurchasePlan).delete()
        for p in plans:
            new_plan = PurchasePlan(
                product_name=p.product_name,
                planned_qty=p.planned_qty,
                plan_date=date.today().isoformat()
            )
            session.add(new_plan)
        session.commit()
        return {"status": "success", "message": f"Saved {len(plans)} plans"}
    finally:
        session.close()

@router.get("/compare/{item_name}")
def compare_mandi_prices(item_name: str):
    session = SessionLocal()
    try:
        item = session.query(Item).filter(Item.name.ilike(item_name)).first()
        if not item:
            vendor_prod = session.query(VendorProduct).filter(VendorProduct.name.ilike(item_name)).first()
            base_p = vendor_prod.purchase_price if vendor_prod else 25.0
            item_id_val = 1
        else:
            base_p = item.base_price
            item_id_val = item.id

        regions = session.query(Region).all()
        comparison = []
        
        for r in regions:
            rng = random.Random(item_id_val * 100 + r.id)
            mult = rng.uniform(0.85, 1.25)
            regional_price = round(base_p * mult, 2)
            comparison.append({
                "region_id": r.id,
                "mandi_name": r.name,
                "state": r.state,
                "wholesale_price": regional_price
            })
            
        comparison.sort(key=lambda x: x["wholesale_price"])
        cheapest = comparison[0] if comparison else None
        
        return {
            "item_name": item_name,
            "comparison": comparison,
            "recommended_mandi": cheapest
        }
    finally:
        session.close()
