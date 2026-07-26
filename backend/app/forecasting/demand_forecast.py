"""
MandiSense Demand Forecasting Module
=====================================
Uses Holt-Winters Exponential Smoothing to forecast next 3 days'
demand for a given item in a given region.

Model choice rationale:
- Holt-Winters handles both trend and weekly seasonality (period=7)
- Simpler and more interpretable than ARIMA for this use case
- No external dependencies beyond statsmodels (vs Prophet needing cmdstan)
- Can be swapped for Prophet/ARIMA by changing the model class

Fallback:
- If data is too sparse (< 14 days), uses a 7-day Simple Moving Average
"""

import sys
import os
import warnings
from datetime import date, timedelta

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.database import SessionLocal
from app.db.models import SalesVolume, Item
from app.config import FORECAST_HISTORY_DAYS, FORECAST_HORIZON, MIN_DATA_FOR_HW, SEASONAL_PERIOD

# Suppress convergence warnings from statsmodels (noisy but harmless)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def get_sales_history(item_id: int, region_id: int, days: int = FORECAST_HISTORY_DAYS) -> pd.DataFrame:
    """
    Fetch the last N days of sales volume data from the database.
    
    Returns a DataFrame indexed by date with 'volume_kg' column.
    """
    session = SessionLocal()
    try:
        cutoff_date = date.today() - timedelta(days=days)
        
        records = (
            session.query(SalesVolume.date, SalesVolume.volume_kg)
            .filter(
                SalesVolume.item_id == item_id,
                SalesVolume.region_id == region_id,
                SalesVolume.date >= cutoff_date,
            )
            .order_by(SalesVolume.date)
            .all()
        )
        
        if not records:
            return pd.DataFrame(columns=["date", "volume_kg"])
        
        df = pd.DataFrame(records, columns=["date", "volume_kg"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        
        # Fill any missing dates with forward fill
        full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq="D")
        df = df.reindex(full_range).ffill().bfill()
        df.index.name = "date"
        
        return df
    finally:
        session.close()


def forecast_demand(item_id: int, region_id: int, horizon: int = FORECAST_HORIZON) -> dict:
    """
    Forecast demand for the next `horizon` days.
    
    Returns:
        {
            "item_id": int,
            "region_id": int,
            "item_name": str,
            "method": "holt_winters" | "simple_moving_average",
            "forecasts": [
                {
                    "date": "YYYY-MM-DD",
                    "predicted_volume": float,
                    "confidence_lower": float,
                    "confidence_upper": float,
                }
            ]
        }
    """
    # Get item name
    session = SessionLocal()
    try:
        item = session.query(Item).filter(Item.id == item_id).first()
        item_name = item.name if item else f"Item #{item_id}"
    finally:
        session.close()
    
    # Fetch history
    history = get_sales_history(item_id, region_id)
    
    if history.empty:
        return {
            "item_id": item_id,
            "region_id": region_id,
            "item_name": item_name,
            "method": "no_data",
            "forecasts": [],
        }
    
    n_points = len(history)
    last_date = history.index.max()
    
    result = {
        "item_id": item_id,
        "region_id": region_id,
        "item_name": item_name,
        "method": "",
        "forecasts": [],
    }
    
    if n_points >= MIN_DATA_FOR_HW:
        # ─── Holt-Winters Exponential Smoothing ─────────────────────────
        try:
            model = ExponentialSmoothing(
                history["volume_kg"],
                trend="add",
                seasonal="add",
                seasonal_periods=SEASONAL_PERIOD,
                initialization_method="estimated",
            )
            fitted = model.fit(optimized=True)
            forecast = fitted.forecast(horizon)
            
            # Approximate confidence interval using residual std dev
            residuals = fitted.resid.dropna()
            std_err = residuals.std() if len(residuals) > 0 else history["volume_kg"].std()
            
            result["method"] = "holt_winters"
            for i, (dt, val) in enumerate(forecast.items()):
                # Widen CI for further-out forecasts
                ci_width = std_err * (1.0 + 0.2 * i) * 1.96
                result["forecasts"].append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "predicted_volume": round(max(0, val), 1),
                    "confidence_lower": round(max(0, val - ci_width), 1),
                    "confidence_upper": round(val + ci_width, 1),
                })
            
        except Exception:
            # Fallback if Holt-Winters fails (can happen with flat data)
            result = _fallback_sma(history, item_id, region_id, item_name, horizon, last_date)
    else:
        # Not enough data for Holt-Winters — use simple moving average
        result = _fallback_sma(history, item_id, region_id, item_name, horizon, last_date)
    
    return result


def _fallback_sma(history: pd.DataFrame, item_id: int, region_id: int,
                   item_name: str, horizon: int, last_date) -> dict:
    """Fallback: 7-day Simple Moving Average forecast."""
    sma = history["volume_kg"].tail(7).mean()
    std = history["volume_kg"].tail(7).std()
    
    result = {
        "item_id": item_id,
        "region_id": region_id,
        "item_name": item_name,
        "method": "simple_moving_average",
        "forecasts": [],
    }
    
    for i in range(horizon):
        forecast_date = last_date + timedelta(days=i + 1)
        result["forecasts"].append({
            "date": forecast_date.strftime("%Y-%m-%d"),
            "predicted_volume": round(max(0, sma), 1),
            "confidence_lower": round(max(0, sma - 1.96 * std), 1),
            "confidence_upper": round(sma + 1.96 * std, 1),
        })
    
    return result
