# SQL Queries Documentation

## Overview

This document outlines the key SQL queries used in the Quick Commerce Analytics platform. All queries are executed using SQLAlchemy ORM with PostgreSQL.

---

## 1. Overview Metrics

### Total Orders
```sql
SELECT COUNT(order_id) FROM orders;
```

### Delivered Orders
```sql
SELECT COUNT(order_id) 
FROM orders 
WHERE status = 'delivered';
```

### Cancelled Orders
```sql
SELECT COUNT(order_id) 
FROM orders 
WHERE status = 'cancelled';
```

### Average Delivery Time
```sql
SELECT AVG(delivery_time_minutes) 
FROM orders 
WHERE status = 'delivered';
```

### Average Delay
```sql
SELECT AVG(delay_minutes) 
FROM orders 
WHERE status = 'delivered' 
AND delay_minutes IS NOT NULL;
```

### On-Time Delivery Rate
```sql
SELECT COUNT(order_id) 
FROM orders 
WHERE status = 'delivered' 
AND delay_minutes <= 5;
```

### Stockout Rate
```sql
-- Total order products
SELECT COUNT(id) FROM order_products;

-- Stockout products
SELECT COUNT(id) 
FROM order_products 
WHERE was_out_of_stock = TRUE;
```

---

## 2. Order Delays Analysis

### Delay Distribution
```sql
SELECT 
    order_id,
    order_datetime,
    promised_delivery_time,
    actual_delivery_time,
    delay_minutes,
    picking_time_minutes,
    s.name AS store_name,
    s.zone
FROM orders o
JOIN stores s ON o.store_id = s.store_id
WHERE o.status = 'delivered'
AND o.delay_minutes IS NOT NULL;
```

### Average Delay by Zone
```sql
SELECT 
    s.zone,
    AVG(o.delay_minutes) AS avg_delay,
    COUNT(o.order_id) AS count
FROM orders o
JOIN stores s ON o.store_id = s.store_id
WHERE o.status = 'delivered'
AND o.delay_minutes IS NOT NULL
GROUP BY s.zone;
```

### Hourly Delay Pattern
```sql
SELECT 
    EXTRACT(HOUR FROM order_datetime) AS hour,
    AVG(delay_minutes) AS avg_delay
FROM orders
WHERE status = 'delivered'
AND delay_minutes IS NOT NULL
GROUP BY EXTRACT(HOUR FROM order_datetime)
ORDER BY hour;
```

### Top Delayed Stores
```sql
SELECT 
    s.name AS store_name,
    AVG(o.delay_minutes) AS avg_delay
FROM orders o
JOIN stores s ON o.store_id = s.store_id
WHERE o.status = 'delivered'
AND o.delay_minutes IS NOT NULL
GROUP BY s.name
ORDER BY avg_delay DESC
LIMIT 5;
```

---

## 3. Cancellation Analysis

### Cancellation Reasons
```sql
SELECT 
    cancellation_reason,
    COUNT(order_id) AS count
FROM orders
WHERE status = 'cancelled'
GROUP BY cancellation_reason;
```

### Cancellations by Zone
```sql
SELECT 
    s.zone,
    COUNT(o.order_id) AS count
FROM orders o
JOIN stores s ON o.store_id = s.store_id
WHERE o.status = 'cancelled'
GROUP BY s.zone;
```

### Cancellation Trend Over Time
```sql
SELECT 
    DATE(order_datetime) AS date,
    COUNT(order_id) AS count
FROM orders
WHERE status = 'cancelled'
GROUP BY DATE(order_datetime)
ORDER BY date;
```

---

## 4. Stockout Analysis

### Top Products with Stockouts
```sql
SELECT 
    p.product_name,
    p.department,
    COUNT(op.id) AS stockout_count
FROM order_products op
JOIN products p ON op.product_id = p.product_id
WHERE op.was_out_of_stock = TRUE
GROUP BY p.product_id, p.product_name, p.department
ORDER BY stockout_count DESC
LIMIT 10;
```

### Stockouts by Department
```sql
SELECT 
    p.department,
    COUNT(op.id) AS stockout_count
FROM order_products op
JOIN products p ON op.product_id = p.product_id
WHERE op.was_out_of_stock = TRUE
GROUP BY p.department;
```

### Store-Level Stockout Analysis
```sql
SELECT 
    s.name,
    s.zone,
    COUNT(op.id) AS stockout_count
FROM stores s
JOIN orders o ON o.store_id = s.store_id
JOIN order_products op ON op.order_id = o.order_id
WHERE op.was_out_of_stock = TRUE
GROUP BY s.store_id, s.name, s.zone;
```

---

## 5. Rider Performance Analysis

### Rider Performance Metrics
```sql
SELECT 
    r.rider_id,
    r.name,
    r.zone,
    r.max_capacity,
    COUNT(o.order_id) AS total_deliveries,
    AVG(o.delivery_time_minutes) AS avg_delivery_time,
    AVG(o.delay_minutes) AS avg_delay
FROM riders r
JOIN orders o ON o.rider_id = r.rider_id
WHERE o.status = 'delivered'
GROUP BY r.rider_id, r.name, r.zone, r.max_capacity;
```

### Top Performing Riders (Lowest Delay)
```sql
SELECT 
    r.name,
    r.zone,
    COUNT(o.order_id) AS total_deliveries,
    AVG(o.delay_minutes) AS avg_delay
FROM riders r
JOIN orders o ON o.rider_id = r.rider_id
WHERE o.status = 'delivered'
GROUP BY r.rider_id, r.name, r.zone
ORDER BY avg_delay ASC
LIMIT 10;
```

### Overloaded Riders (High Volume)
```sql
SELECT 
    r.name,
    r.zone,
    COUNT(o.order_id) AS total_deliveries,
    AVG(o.delay_minutes) AS avg_delay
FROM riders r
JOIN orders o ON o.rider_id = r.rider_id
WHERE o.status = 'delivered'
GROUP BY r.rider_id, r.name, r.zone
ORDER BY total_deliveries DESC
LIMIT 10;
```

### Zone-wise Rider Distribution
```sql
SELECT 
    zone,
    COUNT(rider_id) AS rider_count
FROM riders
GROUP BY zone;
```

---

## 6. Picking Time Analysis

### Stores with Longest Picking Times
```sql
SELECT 
    s.name,
    s.zone,
    AVG(o.picking_time_minutes) AS avg_picking_time,
    COUNT(o.order_id) AS order_count
FROM orders o
JOIN stores s ON o.store_id = s.store_id
WHERE o.status = 'delivered'
GROUP BY s.store_id, s.name, s.zone
ORDER BY avg_picking_time DESC
LIMIT 10;
```

### Picking Time by Order Size
```sql
SELECT 
    total_items,
    AVG(picking_time_minutes) AS avg_picking_time
FROM orders
WHERE status = 'delivered'
GROUP BY total_items
ORDER BY total_items;
```

### Overall Average Picking Time
```sql
SELECT AVG(picking_time_minutes) AS avg_picking_time
FROM orders
WHERE status = 'delivered';
```

---

## 7. Complex Analytical Queries

### Correlation Between Picking Time and Delays
```sql
SELECT 
    CASE 
        WHEN picking_time_minutes < 10 THEN 'Fast (<10 min)'
        WHEN picking_time_minutes BETWEEN 10 AND 15 THEN 'Medium (10-15 min)'
        ELSE 'Slow (>15 min)'
    END AS picking_speed,
    AVG(delay_minutes) AS avg_delay,
    COUNT(order_id) AS order_count
FROM orders
WHERE status = 'delivered'
AND delay_minutes IS NOT NULL
GROUP BY picking_speed;
```

### Peak Hour Analysis
```sql
SELECT 
    EXTRACT(HOUR FROM order_datetime) AS hour,
    COUNT(order_id) AS total_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    AVG(CASE WHEN status = 'delivered' THEN delay_minutes ELSE NULL END) AS avg_delay
FROM orders
GROUP BY EXTRACT(HOUR FROM order_datetime)
ORDER BY hour;
```

### Department Performance
```sql
SELECT 
    p.department,
    COUNT(DISTINCT op.order_id) AS orders_with_product,
    SUM(CASE WHEN op.was_out_of_stock THEN 1 ELSE 0 END) AS stockout_count,
    ROUND(
        SUM(CASE WHEN op.was_out_of_stock THEN 1 ELSE 0 END)::NUMERIC / 
        COUNT(op.id)::NUMERIC * 100, 
        2
    ) AS stockout_rate_percentage
FROM products p
JOIN order_products op ON p.product_id = op.product_id
GROUP BY p.department
ORDER BY stockout_rate_percentage DESC;
```

### Zone Performance Comparison
```sql
SELECT 
    s.zone,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'delivered' THEN o.order_id END) AS delivered,
    COUNT(DISTINCT CASE WHEN o.status = 'cancelled' THEN o.order_id END) AS cancelled,
    AVG(CASE WHEN o.status = 'delivered' THEN o.delay_minutes END) AS avg_delay,
    AVG(CASE WHEN o.status = 'delivered' THEN o.picking_time_minutes END) AS avg_picking_time
FROM stores s
JOIN orders o ON s.store_id = o.store_id
GROUP BY s.zone;
```

---

## Database Optimization Notes

### Indexes Created
```sql
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_store_id ON orders(store_id);
CREATE INDEX idx_orders_rider_id ON orders(rider_id);
CREATE INDEX idx_orders_datetime ON orders(order_datetime);
CREATE INDEX idx_order_products_product_id ON order_products(product_id);
CREATE INDEX idx_order_products_stockout ON order_products(was_out_of_stock);
```

### Query Performance Considerations
- All JOIN operations use indexed foreign keys
- Aggregate functions (AVG, COUNT, SUM) are optimized with proper indexing
- Date-based queries use indexed timestamp columns
- Filtering on status column is indexed for performance

---

## Data Quality Checks

### Missing Data Detection
```sql
SELECT 
    'orders' AS table_name,
    COUNT(*) AS total_records,
    SUM(CASE WHEN actual_delivery_time IS NULL AND status = 'delivered' THEN 1 ELSE 0 END) AS missing_delivery_time,
    SUM(CASE WHEN delay_minutes IS NULL AND status = 'delivered' THEN 1 ELSE 0 END) AS missing_delay
FROM orders;
```

### Data Consistency Check
```sql
SELECT 
    order_id,
    promised_delivery_time,
    actual_delivery_time,
    delay_minutes,
    EXTRACT(EPOCH FROM (actual_delivery_time - promised_delivery_time))/60 AS calculated_delay
FROM orders
WHERE status = 'delivered'
AND ABS(delay_minutes - EXTRACT(EPOCH FROM (actual_delivery_time - promised_delivery_time))/60) > 1
LIMIT 10;
```

---

## Notes

- All queries use parameterized statements via SQLAlchemy to prevent SQL injection
- Timestamps are stored in UTC for consistency
- Delay calculations account for timezone differences
- Null handling is explicit in all aggregate functions
- Performance is optimized through strategic indexing and query structure
