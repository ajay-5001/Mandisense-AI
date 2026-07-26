"""
MandiSense Configuration
========================
Central configuration constants for the application.
All magic numbers and paths are defined here for easy modification.
"""

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # mandisense/backend/
DB_PATH = BASE_DIR / "app" / "db" / "mandisense.db"
OUTPUT_DIR = BASE_DIR / "output"

# ─── Data Generation ─────────────────────────────────────────────────────────
# Date range for synthetic data (12 months)
DATA_START_DATE = "2025-07-01"
DATA_END_DATE = "2026-06-30"

# Number of items and regions
NUM_ITEMS = 15
NUM_REGIONS = 35

# ─── Forecasting ─────────────────────────────────────────────────────────────
# Number of days of history to use for forecasting
FORECAST_HISTORY_DAYS = 90

# Number of days to forecast ahead
FORECAST_HORIZON = 3

# Minimum days of data required for Holt-Winters (fallback to SMA otherwise)
MIN_DATA_FOR_HW = 14

# Weekly seasonality period
SEASONAL_PERIOD = 7

# ─── Spoilage Risk Weights ───────────────────────────────────────────────────
# Must sum to 1.0
RISK_WEIGHT_TEMPERATURE = 0.25
RISK_WEIGHT_HUMIDITY = 0.25
RISK_WEIGHT_SHELF_LIFE = 0.30
RISK_WEIGHT_OVERSUPPLY = 0.20

# Risk level thresholds
RISK_LOW_THRESHOLD = 33      # 0-33: Green (Low)
RISK_MODERATE_THRESHOLD = 66  # 34-66: Yellow (Moderate)
# 67-100: Red (High)
