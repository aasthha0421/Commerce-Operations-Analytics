import random
from datetime import datetime, timedelta
import numpy as np
from database import SessionLocal, Store, Product, Rider, Order, OrderProduct, Inventory, init_db

def generate_sample_data():
    """Generate realistic quick commerce data"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(OrderProduct).delete()
        db.query(Inventory).delete()
        db.query(Order).delete()
        db.query(Rider).delete()
        db.query(Product).delete()
        db.query(Store).delete()
        db.commit()
        
        print("Generating stores...")
        # Create stores
        zones = ['North', 'South', 'East', 'West', 'Central']
        stores = []
        for i in range(1, 11):
            store = Store(
                store_id=i,
                name=f"QuickMart Store {i}",
                zone=random.choice(zones),
                avg_picking_time=random.uniform(5, 20)
            )
            stores.append(store)
            db.add(store)
        db.commit()
        
        print("Generating products...")
        # Create products
        departments = ['Fresh Produce', 'Dairy', 'Bakery', 'Beverages', 'Snacks', 
                      'Frozen Foods', 'Personal Care', 'Household', 'Meat & Seafood']
        products = []
        for i in range(1, 201):
            dept = random.choice(departments)
            product = Product(
                product_id=i,
                product_name=f"Product {i}",
                department=dept,
                aisle=f"Aisle {random.randint(1, 20)}",
                price=random.uniform(2, 50)
            )
            products.append(product)
            db.add(product)
        db.commit()
        
        print("Generating inventory...")
        # Create inventory for each store-product combination
        for store in stores:
            for product in products:
                inventory = Inventory(
                    product_id=product.product_id,
                    store_id=store.store_id,
                    stock_level=random.randint(0, 100),
                    last_updated=datetime.now(),
                    stockout_count=random.randint(0, 10)
                )
                db.add(inventory)
        db.commit()
        
        print("Generating riders...")
        # Create riders
        riders = []
        for i in range(1, 31):
            rider = Rider(
                rider_id=i,
                name=f"Rider {i}",
                zone=random.choice(zones),
                max_capacity=random.randint(3, 6)
            )
            riders.append(rider)
            db.add(rider)
        db.commit()
        
        print("Generating orders...")
        # Create orders (last 3 months)
        start_date = datetime.now() - timedelta(days=90)
        statuses = ['delivered', 'cancelled', 'pending']
        cancellation_reasons = [
            'Out of stock', 'Customer requested', 'Delivery delay', 
            'Payment issue', 'Address not found', 'Weather conditions'
        ]
        
        for i in range(1, 5001):
            order_date = start_date + timedelta(days=random.randint(0, 89),
                                               hours=random.randint(6, 22),
                                               minutes=random.randint(0, 59))
            
            promised_delivery = order_date + timedelta(minutes=random.randint(20, 45))
            status = random.choices(statuses, weights=[0.75, 0.15, 0.10])[0]
            
            picking_time = random.uniform(3, 25)
            total_items = random.randint(3, 25)
            
            # Simulate realistic delays and cancellations
            if status == 'delivered':
                # 60% on time, 40% delayed
                if random.random() < 0.6:
                    actual_delivery = promised_delivery + timedelta(minutes=random.uniform(-5, 5))
                else:
                    actual_delivery = promised_delivery + timedelta(minutes=random.uniform(5, 45))
                
                delay = (actual_delivery - promised_delivery).total_seconds() / 60
                delivery_time = (actual_delivery - order_date).total_seconds() / 60
                cancellation_reason = None
            elif status == 'cancelled':
                actual_delivery = None
                delay = None
                delivery_time = None
                cancellation_reason = random.choice(cancellation_reasons)
            else:  # pending
                actual_delivery = None
                delay = None
                delivery_time = None
                cancellation_reason = None
            
            order = Order(
                order_id=i,
                user_id=random.randint(1, 1000),
                store_id=random.choice(stores).store_id,
                rider_id=random.choice(riders).rider_id,
                order_datetime=order_date,
                promised_delivery_time=promised_delivery,
                actual_delivery_time=actual_delivery,
                status=status,
                cancellation_reason=cancellation_reason,
                total_items=total_items,
                total_amount=random.uniform(20, 200),
                picking_time_minutes=picking_time,
                delivery_time_minutes=delivery_time,
                delay_minutes=delay
            )
            db.add(order)
            
            # Add order products
            selected_products = random.sample(products, min(total_items, len(products)))
            for product in selected_products:
                # Check inventory and simulate stockouts
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == product.product_id,
                    Inventory.store_id == order.store_id
                ).first()
                
                out_of_stock = inventory.stock_level == 0 or random.random() < 0.05
                
                order_product = OrderProduct(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=random.randint(1, 5),
                    was_out_of_stock=out_of_stock
                )
                db.add(order_product)
        
        db.commit()
        print(f"Data generation complete! Created 5000 orders with products.")
        
    except Exception as e:
        print(f"Error generating data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Generating sample data...")
    generate_sample_data()
