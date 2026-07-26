"""
MandiSense Database Models
==========================
SQLAlchemy ORM models for all 5 tables.
Schema is designed to be Postgres-portable (no SQLite-specific types).

Tables:
    - items:        15 perishable items with pricing/shelf-life metadata
    - regions:      3 Indian wholesale market regions
    - daily_prices: wholesale + retail prices per item/region/day
    - weather:      daily weather data per region
    - sales_volume: daily sales volume + footfall per item/region
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Item(Base):
    """
    Perishable item master table.
    
    Contains 15 items (10 vegetables + 5 fruits) with metadata needed
    for pricing and spoilage calculations.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(20), nullable=False)       # 'vegetable' or 'fruit'
    base_price = Column(Float, nullable=False)           # Base wholesale price in INR/kg
    shelf_life_days = Column(Integer, nullable=False)    # Days before spoilage at room temp
    unit = Column(String(10), default="kg")              # Unit of measurement

    # Relationships
    daily_prices = relationship("DailyPrice", back_populates="item")
    sales_volumes = relationship("SalesVolume", back_populates="item")

    def __repr__(self):
        return f"<Item(name='{self.name}', category='{self.category}', base=₹{self.base_price}/kg)>"


class Region(Base):
    """
    Wholesale market region.
    
    Three diverse Indian markets selected to represent different
    climate zones and supply chain dynamics.
    """
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    state = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Relationships
    daily_prices = relationship("DailyPrice", back_populates="region")
    weather_records = relationship("Weather", back_populates="region")
    sales_volumes = relationship("SalesVolume", back_populates="region")

    def __repr__(self):
        return f"<Region(name='{self.name}', state='{self.state}')>"


class DailyPrice(Base):
    """
    Daily wholesale and retail prices per item per region.
    
    One row per (item, region, date) combination.
    Prices are in INR per kg.
    """
    __tablename__ = "daily_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    date = Column(Date, nullable=False)
    wholesale_price = Column(Float, nullable=False)     # INR per kg
    retail_price = Column(Float, nullable=False)         # INR per kg

    # Relationships
    item = relationship("Item", back_populates="daily_prices")
    region = relationship("Region", back_populates="daily_prices")

    def __repr__(self):
        return f"<DailyPrice(item={self.item_id}, region={self.region_id}, date={self.date}, ₹{self.wholesale_price})>"


class Weather(Base):
    """
    Daily weather data per region.
    
    Sourced from simulated climate profiles based on public IMD 
    (India Meteorological Department) averages for each city.
    """
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    date = Column(Date, nullable=False)
    temp_max = Column(Float, nullable=False)         # °C
    temp_min = Column(Float, nullable=False)         # °C
    humidity = Column(Float, nullable=False)          # % (0-100)
    rainfall_mm = Column(Float, nullable=False)      # mm

    # Relationships
    region = relationship("Region", back_populates="weather_records")

    def __repr__(self):
        return f"<Weather(region={self.region_id}, date={self.date}, temp={self.temp_max}°C)>"


class SalesVolume(Base):
    """
    Daily sales volume and footfall per item per region.
    
    Acts as a demand proxy. Volume is in kg, footfall is the 
    estimated number of buyers for that item on that day.
    Footfall is derived from volume / average basket size.
    """
    __tablename__ = "sales_volume"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    date = Column(Date, nullable=False)
    volume_kg = Column(Float, nullable=False)        # kg sold
    footfall = Column(Integer, nullable=False)       # Number of buyers

    # Relationships
    item = relationship("Item", back_populates="sales_volumes")
    region = relationship("Region", back_populates="sales_volumes")

    def __repr__(self):
        return f"<SalesVolume(item={self.item_id}, region={self.region_id}, date={self.date}, {self.volume_kg}kg)>"


class VendorProduct(Base):
    """
    Vendor-specific customized product catalog.
    Supports vegetables, fruits, grains, flowers, spices, etc.
    """
    __tablename__ = "vendor_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    unit = Column(String(20), default="kg")
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    current_stock = Column(Float, nullable=False, default=0.0)
    supplier_name = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<VendorProduct(name='{self.name}', price=₹{self.selling_price}/{self.unit}, stock={self.current_stock})>"


class PurchasePlan(Base):
    """
    Vendor's planned procurement volumes for future planning.
    """
    __tablename__ = "purchase_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(100), nullable=False)
    planned_qty = Column(Float, nullable=False)
    plan_date = Column(String(10), nullable=False)  # YYYY-MM-DD format

    def __repr__(self):
        return f"<PurchasePlan(product='{self.product_name}', qty={self.planned_qty}, date={self.plan_date})>"

