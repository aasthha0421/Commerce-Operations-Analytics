# Quick Commerce Operations & Customer Experience Analytics

A comprehensive analytics platform for analyzing quick commerce operations using SQL, Python (Pandas, NumPy), FastAPI, PostgreSQL, and React.js with Recharts visualizations.

## 🎯 Project Overview

This project analyzes key operational metrics in a quick commerce environment:
- **Order Delays Analysis**: Delivery time patterns, delay distribution by zone and hour
- **Cancellation Analysis**: Reasons, trends, and geographic patterns
- **Stockout Analysis**: Product availability issues by department and store
- **Rider Performance**: Load distribution, efficiency metrics, and performance rankings
- **Picking Time Analysis**: Store efficiency and order size correlation
- **Data-Driven Recommendations**: Automated insights for operational improvements

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (SQL-based analytics)
- **Data Analysis**: Pandas, NumPy, SQLAlchemy
- **Export**: Excel reports with XlsxWriter/OpenPyXL

### Frontend Stack
- **Framework**: React.js
- **Visualization**: Recharts
- **UI Components**: Tailwind CSS, shadcn/ui
- **HTTP Client**: Axios

### Database Schema
- **Stores**: Store locations with zones and performance metrics
- **Products**: Product catalog with departments and aisles
- **Riders**: Delivery personnel with capacity and zone assignments
- **Orders**: Order lifecycle with timestamps and status tracking
- **Order Products**: Line items with stockout tracking
- **Inventory**: Stock levels and stockout history

## 📊 Dataset

The project uses simulated quick commerce data inspired by the Instacart dataset structure, enhanced with operational metrics:
- 5,000 orders over 90 days
- 200 products across 9 departments
- 10 stores in 5 zones
- 30 delivery riders
- Realistic patterns for delays, cancellations, and stockouts

## 🚀 Features

### Analytics Dashboards

1. **Overview Dashboard**
   - Total orders, delivery rate, cancellation rate
   - Average delivery time and delays
   - On-time delivery percentage
   - Stockout rate

2. **Order Delays**
   - Delay distribution (on-time, slight, moderate, severe)
   - Zone-wise delay analysis
   - Hourly delay patterns
   - Top delayed stores

3. **Cancellations**
   - Cancellation reasons breakdown (pie chart)
   - Geographic distribution by zone
   - Time-series trends

4. **Stockouts**
   - Top products with stockout issues
   - Department-level analysis
   - Store-wise stockout tracking

5. **Rider Performance**
   - Top performers (low delay)
   - Overloaded riders (high volume)
   - Zone distribution
   - Load efficiency metrics

6. **Picking Time Analysis**
   - Slowest stores identification
   - Correlation with order size
   - Efficiency benchmarking

7. **Recommendations**
   - Priority-based action items
   - Data-driven operational insights
   - Issue identification and solutions

### Export Functionality
- Excel report generation with multiple worksheets
- Comprehensive data export for offline analysis
- Formatted tables and metrics

## 📁 Project Structure

```
/app
├── backend/
│   ├── server.py              # FastAPI application with analytics endpoints
│   ├── database.py            # SQLAlchemy models and database connection
│   ├── data_generator.py     # Sample data generation script
│   ├── analytics.py           # SQL-based analytics queries and logic
│   ├── excel_export.py        # Excel report generation
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React dashboard component
│   │   ├── App.css            # Styles
│   │   └── index.js           # Entry point
│   ├── package.json           # Node.js dependencies
│   └── .env                   # Frontend environment variables
└── README.md                  # This file
```

## 🔌 API Endpoints

All endpoints are prefixed with `/api/analytics`:

- `GET /api/analytics/overview` - Key performance metrics
- `GET /api/analytics/order-delays` - Delay analysis with patterns
- `GET /api/analytics/cancellations` - Cancellation breakdown
- `GET /api/analytics/stockouts` - Stockout patterns by product/store
- `GET /api/analytics/riders` - Rider performance metrics
- `GET /api/analytics/picking-time` - Store picking time analysis
- `GET /api/analytics/recommendations` - Data-driven recommendations
- `GET /api/analytics/export-excel` - Download Excel report

## 🛠️ Setup & Installation

### Prerequisites
- PostgreSQL 15+
- Python 3.11+
- Node.js 18+
- Yarn package manager

### Backend Setup

```bash
# Navigate to backend directory
cd /app/backend

# Install Python dependencies
pip install -r requirements.txt

# Initialize database and generate sample data
python data_generator.py

# Start the FastAPI server (via supervisor)
sudo supervisorctl restart backend
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd /app/frontend

# Install Node.js dependencies
yarn install

# Start the React development server (via supervisor)
sudo supervisorctl restart frontend
```

## 📈 Key Insights from Analysis

Based on the generated sample data:

1. **Delivery Performance**: ~59% on-time delivery rate with average delay of 10.4 minutes
2. **Cancellations**: 14.5% cancellation rate, primarily due to delivery delays
3. **Stockouts**: 5.7% stockout rate affecting customer satisfaction
4. **Operational Bottlenecks**: 
   - Peak hour delays during 18:00-21:00
   - High-volume riders experiencing increased delays
   - Store picking time averaging 14 minutes

## 🎓 Technical Highlights

### SQL Analytics
- Complex JOINs across multiple tables
- Aggregation functions (COUNT, AVG, SUM)
- GROUP BY for segmentation analysis
- Filtering with WHERE and HAVING clauses
- Date functions for time-series analysis

### Data Processing
- Pandas DataFrames for data manipulation
- NumPy for statistical calculations
- SQLAlchemy ORM for database operations
- Efficient querying with indexing

### Frontend Features
- Responsive design with Tailwind CSS
- Interactive charts with Recharts
- Tab-based navigation
- Real-time data fetching with Axios
- Loading states and error handling

## 📊 Sample SQL Queries

**Order Delay Analysis:**
```sql
SELECT 
    s.zone,
    AVG(o.delay_minutes) as avg_delay,
    COUNT(o.order_id) as order_count
FROM orders o
JOIN stores s ON o.store_id = s.store_id
WHERE o.status = 'delivered'
GROUP BY s.zone;
```

**Stockout Analysis:**
```sql
SELECT 
    p.product_name,
    p.department,
    COUNT(op.id) as stockout_count
FROM order_products op
JOIN products p ON op.product_id = p.product_id
WHERE op.was_out_of_stock = TRUE
GROUP BY p.product_id, p.product_name, p.department
ORDER BY stockout_count DESC
LIMIT 10;
```


---

**Built with**: Python • FastAPI • PostgreSQL • React.js • Pandas • Recharts
