"""
MandiSense Phase 1 Verification Script
========================================
Run this script to verify the entire Phase 1 pipeline:
    1. Seed the database with synthetic data
    2. Query and display sample data from all tables
    3. Run demand forecasts for sample items
    4. Compute spoilage risk scores
    5. Generate charts (saved to backend/output/)

Usage:
    cd mandisense/backend
    python verify_phase1.py
"""

import sys
import os
import io

# Fix Windows console encoding for emoji/unicode output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure imports work from the backend directory
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for chart generation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

from app.config import OUTPUT_DIR
from app.db.database import SessionLocal, create_all_tables
from app.db.models import Item, Region, DailyPrice, Weather, SalesVolume
from app.data.seed_db import seed_database
from app.forecasting.demand_forecast import forecast_demand
from app.forecasting.spoilage_risk import compute_spoilage_risk


def ensure_output_dir():
    """Create output directory for charts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n📁 Charts will be saved to: {OUTPUT_DIR}")


def display_sample_data():
    """Query and display sample rows from each table."""
    session = SessionLocal()
    
    print("\n" + "=" * 60)
    print("📋 SAMPLE DATA FROM ALL TABLES")
    print("=" * 60)
    
    # Items
    print("\n── Items (all 15) ──")
    items = session.query(Item).all()
    for item in items:
        print(f"  {item.id:2d}. {item.name:<15s} | {item.category:<10s} | ₹{item.base_price:>6.0f}/kg | shelf: {item.shelf_life_days:>2d} days")
    
    # Regions
    print("\n── Regions (all 3) ──")
    regions = session.query(Region).all()
    for r in regions:
        print(f"  {r.id}. {r.name:<20s} | {r.state}")
    
    # Prices (last 5 for Tomato in Delhi)
    print("\n── Daily Prices (Tomato, Azadpur — last 5 days) ──")
    prices = (
        session.query(DailyPrice)
        .filter(DailyPrice.item_id == 1, DailyPrice.region_id == 1)
        .order_by(DailyPrice.date.desc())
        .limit(5)
        .all()
    )
    for p in prices:
        print(f"  {p.date} | Wholesale: ₹{p.wholesale_price:>6.1f} | Retail: ₹{p.retail_price:>6.1f}")
    
    # Weather (last 5 for Delhi)
    print("\n── Weather (Azadpur — last 5 days) ──")
    weather = (
        session.query(Weather)
        .filter(Weather.region_id == 1)
        .order_by(Weather.date.desc())
        .limit(5)
        .all()
    )
    for w in weather:
        print(f"  {w.date} | Temp: {w.temp_min:.0f}-{w.temp_max:.0f}°C | Humidity: {w.humidity:.0f}% | Rain: {w.rainfall_mm:.1f}mm")
    
    # Sales Volume (last 5 for Tomato in Delhi)
    print("\n── Sales Volume (Tomato, Azadpur — last 5 days) ──")
    sales = (
        session.query(SalesVolume)
        .filter(SalesVolume.item_id == 1, SalesVolume.region_id == 1)
        .order_by(SalesVolume.date.desc())
        .limit(5)
        .all()
    )
    for s in sales:
        print(f"  {s.date} | Volume: {s.volume_kg:>6.1f} kg | Footfall: {s.footfall:>3d}")
    
    # Row counts
    print("\n── Total Row Counts ──")
    print(f"  Items:        {session.query(Item).count():>8,}")
    print(f"  Regions:      {session.query(Region).count():>8,}")
    print(f"  Daily Prices: {session.query(DailyPrice).count():>8,}")
    print(f"  Weather:      {session.query(Weather).count():>8,}")
    print(f"  Sales Volume: {session.query(SalesVolume).count():>8,}")
    
    session.close()


def run_forecasts():
    """Run demand forecasts for 3 sample items in Azadpur (region 1)."""
    print("\n" + "=" * 60)
    print("🔮 DEMAND FORECASTS (Azadpur Mandi)")
    print("=" * 60)
    
    sample_items = [1, 2, 3]  # Tomato, Onion, Potato
    results = []
    
    for item_id in sample_items:
        forecast = forecast_demand(item_id, region_id=1)
        results.append(forecast)
        
        print(f"\n── {forecast['item_name']} (method: {forecast['method']}) ──")
        for f in forecast["forecasts"]:
            print(f"  {f['date']} | Predicted: {f['predicted_volume']:>6.1f} kg | "
                  f"CI: [{f['confidence_lower']:.1f} — {f['confidence_upper']:.1f}]")
    
    return results


def run_spoilage_risk():
    """Compute spoilage risk for sample items."""
    print("\n" + "=" * 60)
    print("⚠️  SPOILAGE RISK SCORES (Azadpur Mandi)")
    print("=" * 60)
    
    sample_items = [1, 2, 3, 6, 10, 13]  # Tomato, Onion, Potato, Lady Finger, Spinach, Mango
    results = []
    
    for item_id in sample_items:
        risk = compute_spoilage_risk(item_id, region_id=1)
        results.append(risk)
        
        level = risk["risk_level"]
        print(f"\n  {level['emoji']} {risk['item_name']:<15s} | Score: {risk['risk_score']:>5.1f}/100 | {level['label']}")
        
        factors = risk["factors"]
        for name, f in factors.items():
            print(f"     {name:<12s}: {f['score']:>5.1f} × {f['weight']:.0%} = {f['score'] * f['weight']:>5.1f}  ({f['value']})")
    
    return results


def generate_charts(forecast_results: list):
    """Generate and save verification charts."""
    print("\n" + "=" * 60)
    print("📊 GENERATING CHARTS")
    print("=" * 60)
    
    session = SessionLocal()
    
    # ─── Chart 1: Price History (Tomato across all 3 regions) ────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    
    regions = session.query(Region).all()
    colors = ["#e63946", "#457b9d", "#2a9d8f"]
    
    for i, region in enumerate(regions):
        prices = (
            session.query(DailyPrice.date, DailyPrice.wholesale_price)
            .filter(DailyPrice.item_id == 1, DailyPrice.region_id == region.id)
            .order_by(DailyPrice.date)
            .all()
        )
        dates = [p[0] for p in prices]
        values = [p[1] for p in prices]
        
        # 7-day moving average for smoother lines
        df = pd.DataFrame({"date": dates, "price": values})
        df["price_ma"] = df["price"].rolling(7, min_periods=1).mean()
        
        ax.plot(df["date"], df["price_ma"], label=f"{region.name} ({region.state})",
                color=colors[i % len(colors)], linewidth=1.5, alpha=0.9)
    
    ax.set_title("Tomato Wholesale Price — 12 Month History", fontsize=14, fontweight="bold")
    ax.set_ylabel("Price (₹/kg)")
    ax.set_xlabel("Date")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    chart1_path = OUTPUT_DIR / "price_history_tomato.png"
    plt.savefig(chart1_path, dpi=150)
    plt.close()
    print(f"  ✅ Saved: {chart1_path}")
    
    # ─── Chart 2: Demand Forecast (Tomato in Azadpur) ────────────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Historical data (last 30 days for readability)
    sales = (
        session.query(SalesVolume.date, SalesVolume.volume_kg)
        .filter(SalesVolume.item_id == 1, SalesVolume.region_id == 1)
        .order_by(SalesVolume.date.desc())
        .limit(30)
        .all()
    )
    sales.reverse()
    hist_dates = [s[0] for s in sales]
    hist_values = [s[1] for s in sales]
    
    ax.plot(hist_dates, hist_values, color="#457b9d", linewidth=1.5, label="Historical Sales")
    ax.fill_between(hist_dates, hist_values, alpha=0.1, color="#457b9d")
    
    # Forecast overlay
    if forecast_results and forecast_results[0]["forecasts"]:
        fc = forecast_results[0]  # Tomato
        fc_dates = [pd.to_datetime(f["date"]).date() for f in fc["forecasts"]]
        fc_values = [f["predicted_volume"] for f in fc["forecasts"]]
        fc_lower = [f["confidence_lower"] for f in fc["forecasts"]]
        fc_upper = [f["confidence_upper"] for f in fc["forecasts"]]
        
        ax.plot(fc_dates, fc_values, color="#e63946", linewidth=2.5,
                linestyle="--", marker="o", markersize=6, label="Forecast")
        ax.fill_between(fc_dates, fc_lower, fc_upper, alpha=0.2, color="#e63946")
    
    ax.set_title("Tomato Demand — Last 30 Days + 3-Day Forecast (Azadpur)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Volume (kg)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    chart2_path = OUTPUT_DIR / "demand_forecast_tomato.png"
    plt.savefig(chart2_path, dpi=150)
    plt.close()
    print(f"  ✅ Saved: {chart2_path}")
    
    # ─── Chart 3: Spoilage Risk Bar Chart (all items, Azadpur) ──────────
    fig, ax = plt.subplots(figsize=(12, 5))
    
    items = session.query(Item).all()
    risk_scores = []
    item_names = []
    bar_colors = []
    
    for item in items:
        risk = compute_spoilage_risk(item.id, region_id=1)
        risk_scores.append(risk["risk_score"])
        item_names.append(item.name)
        
        # Color by risk level
        if risk["risk_score"] <= 33:
            bar_colors.append("#2a9d8f")  # Green
        elif risk["risk_score"] <= 66:
            bar_colors.append("#e9c46a")  # Yellow
        else:
            bar_colors.append("#e63946")  # Red
    
    bars = ax.barh(item_names, risk_scores, color=bar_colors, edgecolor="white", linewidth=0.5)
    
    # Add score labels
    for bar, score in zip(bars, risk_scores):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{score:.0f}", va="center", fontsize=9)
    
    ax.set_title("Spoilage Risk Scores — All Items (Azadpur Mandi)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Risk Score (0-100)")
    ax.set_xlim(0, 110)
    ax.axvline(x=33, color="#2a9d8f", linestyle=":", alpha=0.5, label="Low threshold")
    ax.axvline(x=66, color="#e9c46a", linestyle=":", alpha=0.5, label="Moderate threshold")
    ax.legend(loc="lower right")
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    
    chart3_path = OUTPUT_DIR / "spoilage_risk_all_items.png"
    plt.savefig(chart3_path, dpi=150)
    plt.close()
    print(f"  ✅ Saved: {chart3_path}")
    
    session.close()


def main():
    """Run the complete Phase 1 verification pipeline."""
    print("\n" + "🌾" * 30)
    print("  MandiSense — Phase 1 Verification")
    print("🌾" * 30)
    
    # Step 1: Seed database
    seed_database()
    
    # Step 2: Display sample data
    display_sample_data()
    
    # Step 3: Run forecasts
    forecast_results = run_forecasts()
    
    # Step 4: Run spoilage risk
    run_spoilage_risk()
    
    # Step 5: Generate charts
    ensure_output_dir()
    generate_charts(forecast_results)
    
    # Done
    print("\n" + "=" * 60)
    print("✅ PHASE 1 VERIFICATION COMPLETE")
    print("=" * 60)
    print("  All components working:")
    print("    ✓ Synthetic data generated (15 items × 3 regions × 365 days)")
    print("    ✓ SQLite database seeded and queryable")
    print("    ✓ Demand forecasting (Holt-Winters) producing predictions")
    print("    ✓ Spoilage risk scoring producing risk levels")
    print("    ✓ Charts saved to output/")
    print("\n  → Ready for Phase 2 (Recommendation Engine)")
    print("=" * 60)


if __name__ == "__main__":
    main()
