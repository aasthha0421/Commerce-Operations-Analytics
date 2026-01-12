from sqlalchemy import func, case, and_, or_
from database import SessionLocal, Order, Product, OrderProduct, Rider, Store, Inventory
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class QuickCommerceAnalytics:
    def __init__(self):
        self.db = SessionLocal()
    
    def close(self):
        self.db.close()
    
    def get_overview_metrics(self):
        """Get key metrics overview"""
        try:
            # Total orders
            total_orders = self.db.query(func.count(Order.order_id)).scalar()
            
            # Delivered orders
            delivered_orders = self.db.query(func.count(Order.order_id)).filter(
                Order.status == 'delivered'
            ).scalar()
            
            # Cancelled orders
            cancelled_orders = self.db.query(func.count(Order.order_id)).filter(
                Order.status == 'cancelled'
            ).scalar()
            
            # Average delivery time
            avg_delivery_time = self.db.query(func.avg(Order.delivery_time_minutes)).filter(
                Order.status == 'delivered'
            ).scalar()
            
            # Average delay
            avg_delay = self.db.query(func.avg(Order.delay_minutes)).filter(
                Order.status == 'delivered',
                Order.delay_minutes.isnot(None)
            ).scalar()
            
            # On-time delivery rate
            on_time = self.db.query(func.count(Order.order_id)).filter(
                Order.status == 'delivered',
                Order.delay_minutes <= 5
            ).scalar()
            
            # Stockout rate
            total_order_products = self.db.query(func.count(OrderProduct.id)).scalar()
            stockout_products = self.db.query(func.count(OrderProduct.id)).filter(
                OrderProduct.was_out_of_stock == True
            ).scalar()
            
            cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
            on_time_rate = (on_time / delivered_orders * 100) if delivered_orders > 0 else 0
            stockout_rate = (stockout_products / total_order_products * 100) if total_order_products > 0 else 0
            
            return {
                'total_orders': total_orders,
                'delivered_orders': delivered_orders,
                'cancelled_orders': cancelled_orders,
                'cancellation_rate': round(cancellation_rate, 2),
                'avg_delivery_time': round(avg_delivery_time, 2) if avg_delivery_time else 0,
                'avg_delay': round(avg_delay, 2) if avg_delay else 0,
                'on_time_rate': round(on_time_rate, 2),
                'stockout_rate': round(stockout_rate, 2)
            }
        except Exception as e:
            print(f"Error in get_overview_metrics: {e}")
            return {}
    
    def get_order_delays_analysis(self):
        """Analyze order delays"""
        try:
            query = self.db.query(
                Order.order_id,
                Order.order_datetime,
                Order.promised_delivery_time,
                Order.actual_delivery_time,
                Order.delay_minutes,
                Order.picking_time_minutes,
                Store.name.label('store_name'),
                Store.zone
            ).join(Store).filter(
                Order.status == 'delivered',
                Order.delay_minutes.isnot(None)
            )
            
            df = pd.read_sql(query.statement, self.db.bind)
            
            # Delay distribution
            delay_ranges = {
                'on_time': len(df[df['delay_minutes'] <= 5]),
                'slight_delay': len(df[(df['delay_minutes'] > 5) & (df['delay_minutes'] <= 15)]),
                'moderate_delay': len(df[(df['delay_minutes'] > 15) & (df['delay_minutes'] <= 30)]),
                'severe_delay': len(df[df['delay_minutes'] > 30])
            }
            
            # Delays by zone
            delays_by_zone = df.groupby('zone')['delay_minutes'].agg([
                ('avg_delay', 'mean'),
                ('count', 'count')
            ]).round(2).to_dict('index')
            
            # Hourly delay pattern
            df['hour'] = pd.to_datetime(df['order_datetime']).dt.hour
            hourly_delays = df.groupby('hour')['delay_minutes'].mean().round(2).to_dict()
            
            return {
                'delay_distribution': delay_ranges,
                'delays_by_zone': delays_by_zone,
                'hourly_delays': hourly_delays,
                'top_delayed_stores': df.groupby('store_name')['delay_minutes'].mean().nlargest(5).round(2).to_dict()
            }
        except Exception as e:
            print(f"Error in get_order_delays_analysis: {e}")
            return {}
    
    def get_cancellation_analysis(self):
        """Analyze order cancellations"""
        try:
            # Cancellation reasons
            reasons = self.db.query(
                Order.cancellation_reason,
                func.count(Order.order_id).label('count')
            ).filter(
                Order.status == 'cancelled'
            ).group_by(Order.cancellation_reason).all()
            
            reason_counts = {r.cancellation_reason: r.count for r in reasons}
            
            # Cancellations by zone
            zone_cancellations = self.db.query(
                Store.zone,
                func.count(Order.order_id).label('count')
            ).join(Store).filter(
                Order.status == 'cancelled'
            ).group_by(Store.zone).all()
            
            zone_data = {z.zone: z.count for z in zone_cancellations}
            
            # Cancellation trend over time
            query = self.db.query(
                func.date(Order.order_datetime).label('date'),
                func.count(Order.order_id).label('count')
            ).filter(
                Order.status == 'cancelled'
            ).group_by(func.date(Order.order_datetime)).order_by('date')
            
            df = pd.read_sql(query.statement, self.db.bind)
            trend = df.to_dict('records')
            
            return {
                'cancellation_reasons': reason_counts,
                'cancellations_by_zone': zone_data,
                'cancellation_trend': trend
            }
        except Exception as e:
            print(f"Error in get_cancellation_analysis: {e}")
            return {}
    
    def get_stockout_analysis(self):
        """Analyze stockout patterns"""
        try:
            # Products with most stockouts
            query = self.db.query(
                Product.product_name,
                Product.department,
                func.count(OrderProduct.id).label('stockout_count')
            ).join(OrderProduct).filter(
                OrderProduct.was_out_of_stock == True
            ).group_by(Product.product_id, Product.product_name, Product.department)
            
            df = pd.read_sql(query.statement, self.db.bind)
            
            # Top products with stockouts
            top_stockout_products = df.nlargest(10, 'stockout_count').to_dict('records')
            
            # Stockouts by department
            stockouts_by_dept = df.groupby('department')['stockout_count'].sum().to_dict()
            
            # Store-level stockout analysis
            store_query = self.db.query(
                Store.name,
                Store.zone,
                func.count(OrderProduct.id).label('stockout_count')
            ).join(Order).join(OrderProduct).filter(
                OrderProduct.was_out_of_stock == True
            ).group_by(Store.store_id, Store.name, Store.zone)
            
            store_df = pd.read_sql(store_query.statement, self.db.bind)
            stockouts_by_store = store_df.to_dict('records')
            
            return {
                'top_stockout_products': top_stockout_products,
                'stockouts_by_department': stockouts_by_dept,
                'stockouts_by_store': stockouts_by_store
            }
        except Exception as e:
            print(f"Error in get_stockout_analysis: {e}")
            return {}
    
    def get_rider_performance(self):
        """Analyze rider performance and load"""
        try:
            query = self.db.query(
                Rider.rider_id,
                Rider.name,
                Rider.zone,
                Rider.max_capacity,
                func.count(Order.order_id).label('total_deliveries'),
                func.avg(Order.delivery_time_minutes).label('avg_delivery_time'),
                func.avg(Order.delay_minutes).label('avg_delay')
            ).join(Order).filter(
                Order.status == 'delivered'
            ).group_by(Rider.rider_id, Rider.name, Rider.zone, Rider.max_capacity)
            
            df = pd.read_sql(query.statement, self.db.bind)
            df = df.round(2)
            
            # Calculate load efficiency (deliveries vs capacity)
            df['load_efficiency'] = (df['total_deliveries'] / df['max_capacity']).round(2)
            
            # Top performers (low delay)
            top_performers = df.nsmallest(10, 'avg_delay')[[
                'name', 'zone', 'total_deliveries', 'avg_delay'
            ]].to_dict('records')
            
            # Overloaded riders (high deliveries)
            overloaded = df.nlargest(10, 'total_deliveries')[[
                'name', 'zone', 'total_deliveries', 'avg_delay'
            ]].to_dict('records')
            
            # Zone-wise rider distribution
            zone_distribution = df.groupby('zone')['rider_id'].count().to_dict()
            
            return {
                'top_performers': top_performers,
                'overloaded_riders': overloaded,
                'zone_distribution': zone_distribution,
                'avg_load_efficiency': round(df['load_efficiency'].mean(), 2)
            }
        except Exception as e:
            print(f"Error in get_rider_performance: {e}")
            return {}
    
    def get_picking_time_analysis(self):
        """Analyze store picking time bottlenecks"""
        try:
            query = self.db.query(
                Store.name,
                Store.zone,
                func.avg(Order.picking_time_minutes).label('avg_picking_time'),
                func.count(Order.order_id).label('order_count')
            ).join(Store).filter(
                Order.status == 'delivered'
            ).group_by(Store.store_id, Store.name, Store.zone)
            
            df = pd.read_sql(query.statement, self.db.bind)
            df = df.round(2)
            
            # Stores with longest picking times
            slowest_stores = df.nlargest(10, 'avg_picking_time').to_dict('records')
            
            # Picking time by order size
            size_query = self.db.query(
                Order.total_items,
                func.avg(Order.picking_time_minutes).label('avg_picking_time')
            ).filter(
                Order.status == 'delivered'
            ).group_by(Order.total_items).order_by(Order.total_items)
            
            size_df = pd.read_sql(size_query.statement, self.db.bind)
            picking_by_size = size_df.to_dict('records')
            
            return {
                'slowest_stores': slowest_stores,
                'picking_time_by_order_size': picking_by_size,
                'avg_picking_time': round(df['avg_picking_time'].mean(), 2)
            }
        except Exception as e:
            print(f"Error in get_picking_time_analysis: {e}")
            return {}
    
    def get_recommendations(self):
        """Generate data-driven recommendations"""
        try:
            overview = self.get_overview_metrics()
            delays = self.get_order_delays_analysis()
            cancellations = self.get_cancellation_analysis()
            stockouts = self.get_stockout_analysis()
            riders = self.get_rider_performance()
            picking = self.get_picking_time_analysis()
            
            recommendations = []
            
            # Delay recommendations
            if overview.get('avg_delay', 0) > 10:
                recommendations.append({
                    'category': 'Delivery Delays',
                    'priority': 'High',
                    'issue': f"Average delay is {overview['avg_delay']} minutes",
                    'recommendation': 'Increase rider capacity during peak hours and optimize routing algorithms'
                })
            
            # Cancellation recommendations
            if overview.get('cancellation_rate', 0) > 10:
                top_reason = max(cancellations.get('cancellation_reasons', {}), 
                               key=cancellations.get('cancellation_reasons', {}).get, default=None)
                if top_reason:
                    recommendations.append({
                        'category': 'Order Cancellations',
                        'priority': 'High',
                        'issue': f"Cancellation rate is {overview['cancellation_rate']}%, mainly due to '{top_reason}'",
                        'recommendation': f"Address '{top_reason}' issue through improved inventory management or customer communication"
                    })
            
            # Stockout recommendations
            if overview.get('stockout_rate', 0) > 5:
                recommendations.append({
                    'category': 'Inventory Stockouts',
                    'priority': 'Critical',
                    'issue': f"Stockout rate is {overview['stockout_rate']}%",
                    'recommendation': 'Implement predictive inventory management and increase safety stock for high-demand items'
                })
            
            # Picking time recommendations
            if picking.get('avg_picking_time', 0) > 15:
                recommendations.append({
                    'category': 'Store Operations',
                    'priority': 'Medium',
                    'issue': f"Average picking time is {picking['avg_picking_time']} minutes",
                    'recommendation': 'Optimize store layout, train staff on efficient picking, and consider automation tools'
                })
            
            # Rider load recommendations
            if len(riders.get('overloaded_riders', [])) > 5:
                recommendations.append({
                    'category': 'Rider Management',
                    'priority': 'High',
                    'issue': 'Multiple riders are handling excessive deliveries',
                    'recommendation': 'Hire additional riders and implement better load balancing across zones'
                })
            
            # On-time delivery recommendations
            if overview.get('on_time_rate', 0) < 70:
                recommendations.append({
                    'category': 'Customer Experience',
                    'priority': 'Critical',
                    'issue': f"Only {overview['on_time_rate']}% of orders delivered on time",
                    'recommendation': 'Review entire fulfillment process, increase buffer time in delivery estimates, and optimize operations'
                })
            
            return recommendations
        except Exception as e:
            print(f"Error in get_recommendations: {e}")
            return []
