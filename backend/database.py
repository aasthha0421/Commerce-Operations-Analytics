from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

POSTGRES_URL = os.environ.get('POSTGRES_URL')

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Store(Base):
    __tablename__ = 'stores'
    
    store_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    zone = Column(String(50))
    avg_picking_time = Column(Float)  # in minutes
    
    orders = relationship('Order', back_populates='store')
    inventory = relationship('Inventory', back_populates='store')

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(200))
    department = Column(String(100))
    aisle = Column(String(100))
    price = Column(Float)
    
    order_products = relationship('OrderProduct', back_populates='product')
    inventory = relationship('Inventory', back_populates='product')

class Rider(Base):
    __tablename__ = 'riders'
    
    rider_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    zone = Column(String(50))
    max_capacity = Column(Integer)  # max orders at once
    
    orders = relationship('Order', back_populates='rider')

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    store_id = Column(Integer, ForeignKey('stores.store_id'))
    rider_id = Column(Integer, ForeignKey('riders.rider_id'))
    order_datetime = Column(DateTime)
    promised_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime, nullable=True)
    status = Column(String(50))  # delivered, cancelled, pending
    cancellation_reason = Column(String(200), nullable=True)
    total_items = Column(Integer)
    total_amount = Column(Float)
    picking_time_minutes = Column(Float)
    delivery_time_minutes = Column(Float, nullable=True)
    delay_minutes = Column(Float, nullable=True)  # actual - promised
    
    store = relationship('Store', back_populates='orders')
    rider = relationship('Rider', back_populates='orders')
    order_products = relationship('OrderProduct', back_populates='order')

class OrderProduct(Base):
    __tablename__ = 'order_products'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    was_out_of_stock = Column(Boolean, default=False)
    
    order = relationship('Order', back_populates='order_products')
    product = relationship('Product', back_populates='order_products')

class Inventory(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'))
    store_id = Column(Integer, ForeignKey('stores.store_id'))
    stock_level = Column(Integer)
    last_updated = Column(DateTime)
    stockout_count = Column(Integer, default=0)
    
    product = relationship('Product', back_populates='inventory')
    store = relationship('Store', back_populates='inventory')

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
