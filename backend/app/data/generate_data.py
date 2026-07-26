"""
MandiSense Synthetic Data Generator
====================================
Generates 12 months of realistic daily data for 15 perishable items
across 3 Indian wholesale market regions.

METHODOLOGY (documented for academic credibility):
----------------------------------------------------
1. PRICES: Base prices sourced from public mandi price averages (agmarknet.gov.in).
   Daily variation uses sinusoidal seasonality (harvest vs off-season), a regional
   cost-of-living multiplier, random walk noise (σ ≈ 3-5%), and event-based spikes
   for festivals (Diwali, Navratri, Pongal) and monsoon supply disruptions.

2. WEATHER: Monthly climate normals derived from IMD (India Meteorological Dept)
   public data for Delhi, Chennai, and Mumbai. Daily values are sampled as
   monthly_mean + gaussian_noise, with realistic physical constraints.

3. SALES VOLUME: Base daily volumes estimated for a mid-sized mandi vendor.
   Includes weekly pattern (weekend spikes), seasonal harvest effects,
   festival demand surges, and rain-dampened footfall.

All random generation uses a fixed seed (42) for reproducibility.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

# Fixed seed for reproducibility
np.random.seed(42)


# ═══════════════════════════════════════════════════════════════════════════════
# ITEM DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════
# Base prices are approximate wholesale prices in INR/kg from agmarknet data.
# Shelf life is at room temperature (no cold chain assumed for small vendors).
# Peak months indicate when the item is in season (0-indexed, Jan=0).

ITEMS_DATA = [
    # Vegetables
    {"name": "Tomato",       "category": "vegetable", "base_price": 25,  "shelf_life_days": 5,  "unit": "kg", "peak_months": [11, 0, 1, 2]},
    {"name": "Onion",        "category": "vegetable", "base_price": 20,  "shelf_life_days": 15, "unit": "kg", "peak_months": [10, 11, 0, 1]},
    {"name": "Potato",       "category": "vegetable", "base_price": 18,  "shelf_life_days": 20, "unit": "kg", "peak_months": [11, 0, 1, 2]},
    {"name": "Cauliflower",  "category": "vegetable", "base_price": 22,  "shelf_life_days": 4,  "unit": "kg", "peak_months": [10, 11, 0, 1]},
    {"name": "Green Chili",  "category": "vegetable", "base_price": 40,  "shelf_life_days": 7,  "unit": "kg", "peak_months": [2, 3, 4, 5]},
    {"name": "Lady Finger",  "category": "vegetable", "base_price": 30,  "shelf_life_days": 3,  "unit": "kg", "peak_months": [3, 4, 5, 6]},
    {"name": "Brinjal",      "category": "vegetable", "base_price": 28,  "shelf_life_days": 5,  "unit": "kg", "peak_months": [9, 10, 11, 0]},
    {"name": "Cabbage",      "category": "vegetable", "base_price": 15,  "shelf_life_days": 7,  "unit": "kg", "peak_months": [10, 11, 0, 1]},
    {"name": "Carrot",       "category": "vegetable", "base_price": 30,  "shelf_life_days": 10, "unit": "kg", "peak_months": [10, 11, 0, 1]},
    {"name": "Spinach",      "category": "vegetable", "base_price": 20,  "shelf_life_days": 2,  "unit": "kg", "peak_months": [10, 11, 0, 1, 2]},
    # Fruits
    {"name": "Banana",       "category": "fruit",     "base_price": 35,  "shelf_life_days": 5,  "unit": "kg", "peak_months": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]},
    {"name": "Apple",        "category": "fruit",     "base_price": 100, "shelf_life_days": 14, "unit": "kg", "peak_months": [7, 8, 9, 10]},
    {"name": "Mango",        "category": "fruit",     "base_price": 60,  "shelf_life_days": 5,  "unit": "kg", "peak_months": [3, 4, 5, 6]},
    {"name": "Papaya",       "category": "fruit",     "base_price": 25,  "shelf_life_days": 4,  "unit": "kg", "peak_months": [9, 10, 11, 0, 1, 2]},
    {"name": "Grapes",       "category": "fruit",     "base_price": 55,  "shelf_life_days": 7,  "unit": "kg", "peak_months": [1, 2, 3, 4]},
]


# ═══════════════════════════════════════════════════════════════════════════════
# REGION DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════
# Three diverse Indian markets selected for different climate zones.
# Price multiplier reflects cost-of-living differences between cities.

CLIMATE_PROFILES = {
    "Northern": {
        0:  [20, 7,  60, 15],    # Jan
        1:  [23, 10, 55, 18],    # Feb
        2:  [30, 15, 40, 12],    # Mar
        3:  [37, 22, 30, 10],    # Apr
        4:  [41, 27, 30, 15],    # May
        5:  [40, 29, 50, 55],    # Jun
        6:  [35, 27, 75, 200],   # Jul (monsoon)
        7:  [34, 26, 78, 220],   # Aug (monsoon)
        8:  [34, 24, 65, 120],   # Sep
        9:  [33, 18, 50, 15],    # Oct
        10: [28, 12, 50, 5],     # Nov
        11: [22, 8,  58, 10],    # Dec
    },
    "Southern": {
        0:  [29, 21, 70, 25],
        1:  [31, 22, 65, 10],
        2:  [33, 24, 60, 8],
        3:  [35, 26, 60, 15],
        4:  [38, 28, 55, 25],
        5:  [37, 28, 55, 50],
        6:  [35, 26, 60, 70],
        7:  [34, 26, 65, 120],
        8:  [34, 25, 70, 130],
        9:  [32, 24, 78, 260],   # NE monsoon
        10: [30, 23, 80, 350],   # NE monsoon peak
        11: [29, 22, 75, 180],
    },
    "Coastal": {
        0:  [31, 19, 60, 2],
        1:  [32, 20, 58, 2],
        2:  [33, 22, 60, 2],
        3:  [34, 25, 65, 5],
        4:  [34, 27, 68, 15],
        5:  [32, 27, 78, 500],   # Monsoon starts
        6:  [30, 26, 85, 800],   # Monsoon peak
        7:  [30, 25, 85, 550],
        8:  [31, 25, 80, 300],
        9:  [33, 24, 72, 80],
        10: [34, 22, 62, 15],
        11: [33, 20, 60, 5],
    },
    "Moderate": {
        0:  [28, 15, 55, 5],
        1:  [30, 17, 50, 5],
        2:  [33, 20, 45, 10],
        3:  [34, 22, 48, 40],
        4:  [33, 21, 55, 110],
        5:  [29, 20, 70, 80],
        6:  [28, 19, 75, 110],
        7:  [28, 19, 78, 140],
        8:  [28, 19, 75, 210],
        9:  [28, 19, 72, 170],
        10: [27, 17, 65, 60],
        11: [26, 15, 60, 15],
    },
    "Desert": {
        0:  [22, 8,  50, 8],
        1:  [26, 11, 45, 12],
        2:  [32, 16, 35, 8],
        3:  [38, 22, 25, 5],
        4:  [42, 27, 25, 15],
        5:  [40, 29, 45, 50],
        6:  [34, 27, 70, 180],
        7:  [32, 26, 75, 200],
        8:  [33, 24, 60, 90],
        9:  [33, 19, 45, 10],
        10: [29, 13, 45, 4],
        11: [24, 9,  50, 5],
    },
    "Hilly": {
        0:  [10, -2, 65, 20],
        1:  [12, 1,  60, 30],
        2:  [18, 5,  55, 35],
        3:  [22, 9,  50, 45],
        4:  [26, 13, 50, 60],
        5:  [25, 15, 65, 150],
        6:  [22, 14, 80, 320],
        7:  [21, 14, 85, 340],
        8:  [21, 12, 75, 180],
        9:  [19, 8,  60, 40],
        10: [15, 3,  60, 15],
        11: [11, 0,  65, 15],
    },
    "Tropical": {
        0:  [26, 14, 65, 15],
        1:  [29, 17, 60, 25],
        2:  [33, 22, 58, 30],
        3:  [36, 25, 62, 50],
        4:  [36, 26, 68, 120],
        5:  [34, 27, 78, 280],
        6:  [32, 26, 83, 390],
        7:  [32, 26, 84, 340],
        8:  [32, 26, 82, 290],
        9:  [31, 24, 75, 160],
        10: [29, 19, 68, 30],
        11: [26, 14, 65, 10],
    }
}

MANDI_LIST = [
    {"name": "Azadpur Mandi", "state": "Delhi", "latitude": 28.7041, "longitude": 77.1025, "price_multiplier": 1.00, "profile": "Northern"},
    {"name": "Koyambedu Wholesale Market", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707, "price_multiplier": 1.05, "profile": "Southern"},
    {"name": "Vashi APMC", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777, "price_multiplier": 1.10, "profile": "Coastal"},
    {"name": "Yeshwanthpur APMC", "state": "Karnataka", "latitude": 13.0286, "longitude": 77.5401, "price_multiplier": 0.98, "profile": "Moderate"},
    {"name": "Jamalpur Market", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714, "price_multiplier": 0.95, "profile": "Desert"},
    {"name": "Bowenpally APMC", "state": "Telangana", "latitude": 17.4374, "longitude": 78.4482, "price_multiplier": 0.96, "profile": "Moderate"},
    {"name": "Madanapalle Tomato Market", "state": "Andhra Pradesh", "latitude": 13.5517, "longitude": 78.5020, "price_multiplier": 0.90, "profile": "Southern"},
    {"name": "Kala Dera Mandi", "state": "Rajasthan", "latitude": 27.2084, "longitude": 75.6339, "price_multiplier": 0.92, "profile": "Desert"},
    {"name": "Kolkata APMC", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639, "price_multiplier": 1.02, "profile": "Tropical"},
    {"name": "Naveen Galla Mandi", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462, "price_multiplier": 0.92, "profile": "Northern"},
    {"name": "Ludhiana APMC", "state": "Punjab", "latitude": 30.9010, "longitude": 75.8573, "price_multiplier": 0.96, "profile": "Northern"},
    {"name": "Karnal Grain Market", "state": "Haryana", "latitude": 29.6857, "longitude": 76.9905, "price_multiplier": 0.94, "profile": "Northern"},
    {"name": "Karond Mandi", "state": "Madhya Pradesh", "latitude": 23.2599, "longitude": 77.4126, "price_multiplier": 0.93, "profile": "Northern"},
    {"name": "Chalai Market", "state": "Kerala", "latitude": 8.4831, "longitude": 76.9536, "price_multiplier": 1.04, "profile": "Coastal"},
    {"name": "Bazar Samiti Mandi", "state": "Bihar", "latitude": 25.5941, "longitude": 85.1376, "price_multiplier": 0.88, "profile": "Tropical"},
    {"name": "Chhatra Bazar", "state": "Odisha", "latitude": 20.4625, "longitude": 85.8830, "price_multiplier": 0.90, "profile": "Tropical"},
    {"name": "Pamohi APMC", "state": "Assam", "latitude": 26.1158, "longitude": 91.7086, "price_multiplier": 0.95, "profile": "Tropical"},
    {"name": "Krishi Upaj Mandi", "state": "Jharkhand", "latitude": 23.3441, "longitude": 85.3096, "price_multiplier": 0.92, "profile": "Tropical"},
    {"name": "Pandri Mandi", "state": "Chhattisgarh", "latitude": 21.2514, "longitude": 81.6296, "price_multiplier": 0.91, "profile": "Tropical"},
    {"name": "Niranjanpur Mandi", "state": "Uttarakhand", "latitude": 30.3165, "longitude": 78.0322, "price_multiplier": 0.95, "profile": "Hilly"},
    {"name": "Dhalli Mandi", "state": "Himachal Pradesh", "latitude": 31.1048, "longitude": 77.1734, "price_multiplier": 0.96, "profile": "Hilly"},
    {"name": "Narwal Fruit Market", "state": "Jammu & Kashmir", "latitude": 32.7266, "longitude": 74.8570, "price_multiplier": 0.98, "profile": "Hilly"},
    {"name": "Panaji APMC", "state": "Goa", "latitude": 15.4909, "longitude": 73.8278, "price_multiplier": 1.08, "profile": "Coastal"},
    {"name": "Khwairamband Bazar", "state": "Manipur", "latitude": 24.8170, "longitude": 93.9368, "price_multiplier": 0.96, "profile": "Hilly"},
    {"name": "Maharajganj Bazar", "state": "Tripura", "latitude": 23.8315, "longitude": 91.2868, "price_multiplier": 0.94, "profile": "Tropical"},
    {"name": "Iewduh Market", "state": "Meghalaya", "latitude": 25.5714, "longitude": 91.8803, "price_multiplier": 0.95, "profile": "Hilly"},
    {"name": "Dimapur APMC", "state": "Nagaland", "latitude": 25.9064, "longitude": 93.7274, "price_multiplier": 0.97, "profile": "Hilly"},
    {"name": "Bara Bazar", "state": "Mizoram", "latitude": 23.7271, "longitude": 92.7176, "price_multiplier": 0.98, "profile": "Hilly"},
    {"name": "Lal Market", "state": "Sikkim", "latitude": 27.3314, "longitude": 88.6138, "price_multiplier": 0.99, "profile": "Hilly"},
    {"name": "Puducherry Grand Market", "state": "Puducherry", "latitude": 11.9416, "longitude": 79.8083, "price_multiplier": 1.01, "profile": "Southern"},
    {"name": "Sector 26 APMC", "state": "Chandigarh", "latitude": 30.7333, "longitude": 76.7794, "price_multiplier": 1.02, "profile": "Northern"},
    {"name": "Leh Vegetable Market", "state": "Ladakh", "latitude": 34.1526, "longitude": 77.5771, "price_multiplier": 1.15, "profile": "Hilly"},
    {"name": "Port Blair APMC", "state": "Andaman & Nicobar", "latitude": 11.6234, "longitude": 92.7265, "price_multiplier": 1.20, "profile": "Coastal"},
    {"name": "Daman APMC", "state": "Dadra and Nagar Haveli and Daman and Diu", "latitude": 20.3974, "longitude": 72.8328, "price_multiplier": 1.05, "profile": "Coastal"},
    {"name": "Kavaratti Market", "state": "Lakshadweep", "latitude": 10.5667, "longitude": 72.6417, "price_multiplier": 1.25, "profile": "Coastal"}
]

REGIONS_DATA = []
for idx, mandi in enumerate(MANDI_LIST):
    REGIONS_DATA.append({
        "id": idx + 1,
        "name": mandi["name"],
        "state": mandi["state"],
        "latitude": mandi["latitude"],
        "longitude": mandi["longitude"],
        "price_multiplier": mandi["price_multiplier"],
        "climate": CLIMATE_PROFILES[mandi["profile"]]
    })


# ═══════════════════════════════════════════════════════════════════════════════
# FESTIVAL / EVENT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════
# Major Indian festivals that cause demand spikes in perishable goods.
# Dates are approximate for the simulation period (2025-2026).

FESTIVAL_PERIODS = [
    {"name": "Navratri",     "start": date(2025, 10, 2),  "end": date(2025, 10, 12), "demand_boost": 0.30},
    {"name": "Diwali",       "start": date(2025, 10, 20), "end": date(2025, 10, 25), "demand_boost": 0.40},
    {"name": "Christmas",    "start": date(2025, 12, 23), "end": date(2025, 12, 26), "demand_boost": 0.15},
    {"name": "Pongal",       "start": date(2026, 1, 14),  "end": date(2026, 1, 17),  "demand_boost": 0.25},
    {"name": "Holi",         "start": date(2026, 3, 13),  "end": date(2026, 3, 15),  "demand_boost": 0.20},
    {"name": "Ugadi",        "start": date(2026, 3, 29),  "end": date(2026, 3, 30),  "demand_boost": 0.15},
    {"name": "Ram Navami",   "start": date(2026, 4, 6),   "end": date(2026, 4, 7),   "demand_boost": 0.15},
]


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_date_range(start_str: str, end_str: str) -> list:
    """Generate a list of dates from start to end (inclusive)."""
    start = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def is_festival(d: date) -> tuple:
    """Check if a date falls within a festival period. Returns (is_festival, boost)."""
    for fest in FESTIVAL_PERIODS:
        if fest["start"] <= d <= fest["end"]:
            return True, fest["demand_boost"]
    return False, 0.0


def is_monsoon_disruption(d: date, region_name: str) -> bool:
    """
    Simulate random supply disruption events during monsoon.
    ~12% chance of disruption on any monsoon day, lasting 1 day.
    """
    month = d.month
    # Monsoon months differ by region (NE monsoon for Chennai/Madanapalle, SW for rest)
    if "Tamil Nadu" in region_name or "Andhra" in region_name:
        if month in [10, 11, 12]:
            return np.random.random() < 0.12
    else:
        if month in [6, 7, 8, 9]:
            return np.random.random() < 0.12
    return False


def get_seasonal_factor(d: date, peak_months: list) -> float:
    """
    Returns a seasonal price/volume factor based on whether the item
    is in-season or off-season.
    
    In-season (peak):   factor close to 1.0 (low price, high volume)
    Off-season:         factor > 1.0 for price, < 1.0 for volume
    
    Uses a smooth cosine transition rather than a hard cutoff.
    """
    month_0indexed = d.month - 1  # Convert to 0-indexed
    
    if month_0indexed in peak_months:
        # In season — prices lower, volume higher
        return 0.0  # No off-season markup
    else:
        # Off season — find distance to nearest peak month
        min_dist = min(
            min(abs(month_0indexed - pm), 12 - abs(month_0indexed - pm))
            for pm in peak_months
        )
        # Normalize to 0-1 (max distance is 6 months)
        return min(min_dist / 6.0, 1.0) * 0.40  # Up to 40% off-season markup


def generate_items_df() -> pd.DataFrame:
    """Generate the items master DataFrame."""
    records = []
    for i, item in enumerate(ITEMS_DATA, 1):
        records.append({
            "id": i,
            "name": item["name"],
            "category": item["category"],
            "base_price": item["base_price"],
            "shelf_life_days": item["shelf_life_days"],
            "unit": item["unit"],
        })
    return pd.DataFrame(records)


def generate_regions_df() -> pd.DataFrame:
    """Generate the regions master DataFrame."""
    records = []
    for i, region in enumerate(REGIONS_DATA, 1):
        records.append({
            "id": i,
            "name": region["name"],
            "state": region["state"],
            "latitude": region["latitude"],
            "longitude": region["longitude"],
        })
    return pd.DataFrame(records)


def generate_weather_df(dates: list) -> pd.DataFrame:
    """
    Generate daily weather data for all regions.
    
    Logic:
    - Start from monthly climate normals (from IMD public data)
    - Add gaussian noise for daily variation
    - Clamp to physically realistic ranges
    """
    records = []
    for r_idx, region in enumerate(REGIONS_DATA, 1):
        climate = region["climate"]
        for d in dates:
            month_0indexed = d.month - 1
            base_temp_max, base_temp_min, base_humidity, base_rainfall = climate[month_0indexed]
            
            # Daily variation with gaussian noise
            temp_max = base_temp_max + np.random.normal(0, 2.0)
            temp_min = base_temp_min + np.random.normal(0, 1.5)
            humidity = base_humidity + np.random.normal(0, 8.0)
            
            # Rainfall: most days are 0 in dry months, use exponential dist in monsoon
            if base_rainfall > 50:
                # Rainy month: ~40% chance of rain on any given day
                if np.random.random() < 0.40:
                    rainfall = np.random.exponential(base_rainfall / 12)
                else:
                    rainfall = 0.0
            elif base_rainfall > 10:
                if np.random.random() < 0.15:
                    rainfall = np.random.exponential(base_rainfall / 5)
                else:
                    rainfall = 0.0
            else:
                if np.random.random() < 0.05:
                    rainfall = np.random.exponential(3.0)
                else:
                    rainfall = 0.0
            
            # Clamp to realistic ranges
            temp_max = np.clip(temp_max, 10, 48)
            temp_min = np.clip(temp_min, 5, min(temp_max - 2, 35))
            humidity = np.clip(humidity, 20, 98)
            rainfall = np.clip(rainfall, 0, 120)
            
            records.append({
                "region_id": r_idx,
                "date": d,
                "temp_max": round(temp_max, 1),
                "temp_min": round(temp_min, 1),
                "humidity": round(humidity, 1),
                "rainfall_mm": round(rainfall, 1),
            })
    
    return pd.DataFrame(records)


def generate_daily_prices_df(dates: list) -> pd.DataFrame:
    """
    Generate daily wholesale and retail prices for all item-region pairs.
    
    Price formula:
        price = base_price × regional_multiplier × (1 + seasonal_factor)
                + random_walk_noise + festival_spike + monsoon_disruption_spike
    
    Retail = wholesale × markup (1.3 to 1.5, item-dependent)
    """
    records = []
    
    # Item-specific retail markup (higher for short shelf-life items)
    markups = {}
    for item in ITEMS_DATA:
        if item["shelf_life_days"] <= 3:
            markups[item["name"]] = 1.50  # High markup for very perishable
        elif item["shelf_life_days"] <= 7:
            markups[item["name"]] = 1.40
        else:
            markups[item["name"]] = 1.30
    
    for r_idx, region in enumerate(REGIONS_DATA, 1):
        price_mult = region["price_multiplier"]
        
        for i_idx, item in enumerate(ITEMS_DATA, 1):
            base = item["base_price"]
            peak_months = item["peak_months"]
            markup = markups[item["name"]]
            
            # Initialize random walk from base price
            prev_price = base * price_mult
            
            for d in dates:
                # Seasonal factor
                seasonal = get_seasonal_factor(d, peak_months)
                
                # Random walk (mean-reverting around base × seasonal)
                target_price = base * price_mult * (1 + seasonal)
                noise = np.random.normal(0, base * 0.03)  # ~3% daily noise
                
                # Mean reversion: pull back toward target
                reversion = 0.1 * (target_price - prev_price)
                wholesale = prev_price + reversion + noise
                
                # Festival spike
                is_fest, boost = is_festival(d)
                if is_fest:
                    wholesale *= (1 + boost * 0.5)  # Prices rise with demand
                
                # Monsoon supply disruption spike
                if is_monsoon_disruption(d, region["name"]):
                    wholesale *= 1.20  # +20% due to supply shortage
                
                # Floor price: never below 60% of base
                wholesale = max(wholesale, base * 0.6)
                
                # Round to nearest 0.5 (realistic price granularity)
                wholesale = round(wholesale * 2) / 2
                retail = round(wholesale * markup * 2) / 2
                
                prev_price = wholesale  # Carry forward for random walk
                
                records.append({
                    "item_id": i_idx,
                    "region_id": r_idx,
                    "date": d,
                    "wholesale_price": wholesale,
                    "retail_price": retail,
                })
    
    return pd.DataFrame(records)


def generate_sales_volume_df(dates: list, weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate daily sales volume and footfall for all item-region pairs.
    
    Volume formula:
        volume = base_volume × seasonal_factor × weekend_factor
                 × festival_factor × weather_factor + noise
    
    Footfall = volume / avg_basket_size (estimated per item)
    """
    # Base daily volumes in kg for a mid-sized vendor
    base_volumes = {
        "Tomato": 80, "Onion": 100, "Potato": 120, "Cauliflower": 50,
        "Green Chili": 25, "Lady Finger": 40, "Brinjal": 45, "Cabbage": 60,
        "Carrot": 40, "Spinach": 30, "Banana": 70, "Apple": 35,
        "Mango": 55, "Papaya": 35, "Grapes": 30,
    }
    
    # Average basket size per item (kg per buyer)
    basket_sizes = {
        "Tomato": 1.5, "Onion": 2.0, "Potato": 2.5, "Cauliflower": 1.0,
        "Green Chili": 0.25, "Lady Finger": 0.5, "Brinjal": 0.75, "Cabbage": 1.0,
        "Carrot": 0.75, "Spinach": 0.5, "Banana": 1.5, "Apple": 1.0,
        "Mango": 1.5, "Papaya": 1.0, "Grapes": 0.75,
    }
    
    # Pre-index weather for fast lookup: (region_id, date) -> rainfall
    weather_lookup = {}
    for _, row in weather_df.iterrows():
        weather_lookup[(row["region_id"], row["date"])] = row["rainfall_mm"]
    
    records = []
    
    for r_idx, region in enumerate(REGIONS_DATA, 1):
        for i_idx, item in enumerate(ITEMS_DATA, 1):
            base_vol = base_volumes[item["name"]]
            basket = basket_sizes[item["name"]]
            peak_months = item["peak_months"]
            
            for d in dates:
                volume = base_vol
                
                # 1. Seasonal factor: in-season = +20% volume, off-season = -30%
                month_0 = d.month - 1
                if month_0 in peak_months:
                    volume *= 1.20
                else:
                    seasonal_off = get_seasonal_factor(d, peak_months)
                    volume *= (1.0 - seasonal_off * 0.75)
                
                # 2. Weekend spike: Saturday +15%, Sunday +10%
                weekday = d.weekday()
                if weekday == 5:    # Saturday
                    volume *= 1.15
                elif weekday == 6:  # Sunday
                    volume *= 1.10
                
                # 3. Festival demand surge
                is_fest, boost = is_festival(d)
                if is_fest:
                    volume *= (1 + boost)
                
                # 4. Rain dampening: heavy rain reduces footfall
                rainfall = weather_lookup.get((r_idx, d), 0)
                if rainfall > 20:
                    volume *= 0.70  # -30% on heavy rain days
                elif rainfall > 5:
                    volume *= 0.85  # -15% on moderate rain
                
                # 5. Random noise ±10%
                volume *= (1 + np.random.normal(0, 0.10))
                
                # Floor: minimum 5 kg
                volume = max(volume, 5.0)
                volume = round(volume, 1)
                
                # Footfall from volume
                footfall = max(1, int(volume / basket))
                
                records.append({
                    "item_id": i_idx,
                    "region_id": r_idx,
                    "date": d,
                    "volume_kg": volume,
                    "footfall": footfall,
                })
    
    return pd.DataFrame(records)


def generate_all_data(start_date: str, end_date: str) -> dict:
    """
    Master function: generate all synthetic data.
    
    Returns a dict of DataFrames ready for database insertion.
    """
    print("📊 MandiSense Synthetic Data Generator")
    print("=" * 50)
    
    dates = generate_date_range(start_date, end_date)
    print(f"  Date range: {dates[0]} to {dates[-1]} ({len(dates)} days)")
    
    print("  Generating items master data...")
    items_df = generate_items_df()
    
    print("  Generating regions master data...")
    regions_df = generate_regions_df()
    
    print("  Generating weather data...")
    weather_df = generate_weather_df(dates)
    print(f"    → {len(weather_df):,} weather records")
    
    print("  Generating daily prices...")
    prices_df = generate_daily_prices_df(dates)
    print(f"    → {len(prices_df):,} price records")
    
    print("  Generating sales volume...")
    sales_df = generate_sales_volume_df(dates, weather_df)
    print(f"    → {len(sales_df):,} sales records")
    
    print("=" * 50)
    total = len(items_df) + len(regions_df) + len(weather_df) + len(prices_df) + len(sales_df)
    print(f"  ✅ Total records generated: {total:,}")
    
    return {
        "items": items_df,
        "regions": regions_df,
        "weather": weather_df,
        "daily_prices": prices_df,
        "sales_volume": sales_df,
    }
