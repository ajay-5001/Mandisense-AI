"""
MandiSense Database Seeder
==========================
Loads synthetic data into the SQLite database.
Idempotent: drops and recreates all tables on each run.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.database import engine, create_all_tables, drop_all_tables, SessionLocal
from app.db.models import Item, Region, DailyPrice, Weather, SalesVolume, VendorProduct
from app.data.generate_data import generate_all_data
from app.config import DATA_START_DATE, DATA_END_DATE


def seed_database():
    """
    Generate synthetic data and load it into the SQLite database.
    
    This is idempotent — it drops all existing tables and recreates them,
    then bulk-inserts the generated data.
    """
    print("\n🗄️  MandiSense Database Seeder")
    print("=" * 50)
    
    # Step 1: Reset database
    print("  Dropping existing tables...")
    drop_all_tables()
    print("  Creating fresh tables...")
    create_all_tables()
    
    # Step 2: Generate synthetic data
    data = generate_all_data(DATA_START_DATE, DATA_END_DATE)
    
    # Step 3: Insert into database
    session = SessionLocal()
    
    try:
        # Insert items
        print("\n  Loading items into database...")
        for _, row in data["items"].iterrows():
            session.add(Item(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                base_price=row["base_price"],
                shelf_life_days=row["shelf_life_days"],
                unit=row["unit"],
            ))
        session.flush()
        
        # Insert regions
        print("  Loading regions into database...")
        for _, row in data["regions"].iterrows():
            session.add(Region(
                id=row["id"],
                name=row["name"],
                state=row["state"],
                latitude=row["latitude"],
                longitude=row["longitude"],
            ))
        session.flush()
        
        # Insert weather (bulk insert for speed)
        print("  Loading weather data...")
        weather_records = [
            Weather(
                region_id=int(row["region_id"]),
                date=row["date"],
                temp_max=row["temp_max"],
                temp_min=row["temp_min"],
                humidity=row["humidity"],
                rainfall_mm=row["rainfall_mm"],
            )
            for _, row in data["weather"].iterrows()
        ]
        session.bulk_save_objects(weather_records)
        session.flush()
        
        # Insert daily prices (bulk insert)
        print("  Loading daily prices...")
        price_records = [
            DailyPrice(
                item_id=int(row["item_id"]),
                region_id=int(row["region_id"]),
                date=row["date"],
                wholesale_price=row["wholesale_price"],
                retail_price=row["retail_price"],
            )
            for _, row in data["daily_prices"].iterrows()
        ]
        session.bulk_save_objects(price_records)
        session.flush()
        
        # Insert sales volume (bulk insert)
        print("  Loading sales volume data...")
        sales_records = [
            SalesVolume(
                item_id=int(row["item_id"]),
                region_id=int(row["region_id"]),
                date=row["date"],
                volume_kg=row["volume_kg"],
                footfall=int(row["footfall"]),
            )
            for _, row in data["sales_volume"].iterrows()
        ]
        session.bulk_save_objects(sales_records)
        session.flush()
        
        # Seed default vendor products
        print("  Seeding default vendor products...")
        default_vendor_products = [
            VendorProduct(name="Tomato", category="vegetable", unit="kg", purchase_price=25.0, selling_price=35.0, current_stock=50.0, supplier_name="Azadpur Farm Direct"),
            VendorProduct(name="Onion", category="vegetable", unit="kg", purchase_price=20.0, selling_price=28.0, current_stock=80.0, supplier_name="Nashik Mandi Union"),
            VendorProduct(name="Potato", category="vegetable", unit="kg", purchase_price=18.0, selling_price=25.0, current_stock=120.0, supplier_name="UP Cold Storage Co"),
            VendorProduct(name="Banana", category="fruit", unit="kg", purchase_price=35.0, selling_price=45.0, current_stock=40.0, supplier_name="Kalyan Fruit Wholesalers"),
            VendorProduct(name="Apple", category="fruit", unit="kg", purchase_price=100.0, selling_price=130.0, current_stock=30.0, supplier_name="Himachal Orchard Union"),
        ]
        session.add_all(default_vendor_products)
        session.flush()
        
        # Commit all
        print("\n  Committing to database...")
        session.commit()
        
        # Verify counts
        print("\n  📊 Verification:")
        print(f"    Items:        {session.query(Item).count()} rows")
        print(f"    Regions:      {session.query(Region).count()} rows")
        print(f"    Weather:      {session.query(Weather).count():,} rows")
        print(f"    Daily Prices: {session.query(DailyPrice).count():,} rows")
        print(f"    Sales Volume: {session.query(SalesVolume).count():,} rows")
        print("\n  ✅ Database seeded successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"\n  ❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
