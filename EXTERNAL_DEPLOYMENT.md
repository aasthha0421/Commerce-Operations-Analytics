# External Deployment Guide

## Quick Commerce Analytics Platform - External Deployment

This guide covers deploying the PostgreSQL-based analytics platform to external hosting providers.

---

## Deployment Options

### Option 1: Heroku (Easiest)
### Option 2: DigitalOcean App Platform
### Option 3: AWS (EC2 + RDS)
### Option 4: Railway
### Option 5: Render
### Option 6: Docker Compose (Any VPS)

---

## Prerequisites

- Git repository with your code
- Account on chosen platform
- PostgreSQL database (most platforms provide managed PostgreSQL)
- Node.js 18+ and Python 3.11+ support

---

## 1. Heroku Deployment

### Step 1: Install Heroku CLI
```bash
# MacOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Login and Create App
```bash
heroku login
heroku create your-analytics-app
```

### Step 3: Add PostgreSQL Add-on
```bash
heroku addons:create heroku-postgresql:mini
```

### Step 4: Set Environment Variables
```bash
# Backend variables
heroku config:set MONGO_URL="mongodb://localhost:27017" # Optional, for status checks only
heroku config:set DB_NAME="test_database"
heroku config:set CORS_ORIGINS="*"
# POSTGRES_URL is automatically set by Heroku PostgreSQL addon

# Frontend variables (replace with your Heroku app URL)
heroku config:set REACT_APP_BACKEND_URL="https://your-analytics-app.herokuapp.com"
```

### Step 5: Create Procfile
```bash
cat > Procfile << 'EOF'
web: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
release: cd backend && python data_generator.py
EOF
```

### Step 6: Create requirements.txt for Heroku
```bash
cat > requirements.txt << 'EOF'
fastapi==0.110.1
uvicorn==0.25.0
psycopg2-binary==2.9.11
sqlalchemy==2.0.45
pandas==2.3.3
numpy==2.4.0
openpyxl==3.1.5
xlsxwriter==3.2.9
scipy==1.17.0
python-dotenv==1.0.1
motor==3.3.1
pymongo==4.5.0
pydantic>=2.6.4
EOF
```

### Step 7: Deploy
```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### Step 8: Scale and Open
```bash
heroku ps:scale web=1
heroku open
```

---

## 2. DigitalOcean App Platform

### Step 1: Create Account
- Go to https://cloud.digitalocean.com/
- Create new account or sign in

### Step 2: Create App
1. Click "Create" → "Apps"
2. Connect your GitHub repository
3. Select branch (main/master)

### Step 3: Configure Backend
```yaml
name: analytics-backend
environment_slug: python
build_command: |
  cd backend
  pip install -r requirements.txt
run_command: cd backend && uvicorn server:app --host 0.0.0.0 --port 8080
http_port: 8080

envs:
  - key: POSTGRES_URL
    scope: RUN_TIME
    value: ${db.DATABASE_URL}
  - key: CORS_ORIGINS
    scope: RUN_TIME
    value: "*"
```

### Step 4: Configure Frontend
```yaml
name: analytics-frontend
environment_slug: node-js
build_command: |
  cd frontend
  yarn install
  yarn build
run_command: cd frontend && yarn start
http_port: 3000

envs:
  - key: REACT_APP_BACKEND_URL
    scope: BUILD_TIME
    value: ${analytics-backend.PUBLIC_URL}
```

### Step 5: Add PostgreSQL Database
1. In App Platform, click "Add Resource"
2. Select "Database"
3. Choose PostgreSQL
4. Select plan (Dev Database is free)

### Step 6: Deploy
- Click "Deploy"
- Wait for build to complete
- App will be available at: `https://your-app.ondigitalocean.app`

---

## 3. AWS Deployment (EC2 + RDS)

### Step 1: Create RDS PostgreSQL Instance
```bash
aws rds create-db-instance \
  --db-instance-identifier analytics-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword123 \
  --allocated-storage 20
```

### Step 2: Launch EC2 Instance
```bash
# Launch Ubuntu 22.04 instance
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t2.medium \
  --key-name your-key-pair \
  --security-groups analytics-sg
```

### Step 3: SSH into EC2 and Setup
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm postgresql-client

# Install Python packages
pip3 install -r backend/requirements.txt

# Install Node packages
cd frontend && npm install && npm run build && cd ..

# Setup environment variables
cat > backend/.env << EOF
POSTGRES_URL="postgresql://admin:YourPassword@your-rds-endpoint:5432/analytics"
CORS_ORIGINS="*"
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
EOF

cat > frontend/.env << EOF
REACT_APP_BACKEND_URL="http://your-ec2-ip:8001"
EOF

# Initialize database
cd backend && python3 data_generator.py

# Start services with PM2
npm install -g pm2
pm2 start "uvicorn server:app --host 0.0.0.0 --port 8001" --name backend
pm2 start "npm start" --name frontend --cwd ../frontend
pm2 startup
pm2 save
```

### Step 4: Configure Security Groups
```bash
# Allow inbound traffic
aws ec2 authorize-security-group-ingress \
  --group-name analytics-sg \
  --protocol tcp --port 8001 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name analytics-sg \
  --protocol tcp --port 3000 --cidr 0.0.0.0/0
```

---

## 4. Railway Deployment

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

### Step 2: Initialize Project
```bash
railway init
railway link
```

### Step 3: Add PostgreSQL
```bash
railway add --plugin postgresql
```

### Step 4: Set Environment Variables
```bash
railway variables set CORS_ORIGINS="*"
railway variables set REACT_APP_BACKEND_URL="https://your-app.railway.app"
```

### Step 5: Create railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 6: Deploy
```bash
railway up
```

---

## 5. Render Deployment

### Step 1: Create Account
- Go to https://render.com/
- Sign up or log in

### Step 2: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Choose free tier
3. Note the connection string

### Step 3: Create Web Service (Backend)
```yaml
name: analytics-backend
env: python
buildCommand: cd backend && pip install -r requirements.txt
startCommand: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT

environment:
  - key: POSTGRES_URL
    value: <your-postgres-connection-string>
  - key: CORS_ORIGINS
    value: "*"
```

### Step 4: Create Web Service (Frontend)
```yaml
name: analytics-frontend
env: node
buildCommand: cd frontend && yarn install && yarn build
startCommand: cd frontend && yarn start

environment:
  - key: REACT_APP_BACKEND_URL
    value: https://analytics-backend.onrender.com
```

### Step 5: Deploy
- Push to GitHub
- Render auto-deploys on push

---

## 6. Docker Compose Deployment (Any VPS)

### Step 1: Create docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: quickcommerce
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      POSTGRES_URL: postgresql://postgres:postgres@postgres:5432/quickcommerce
      CORS_ORIGINS: "*"
    depends_on:
      - postgres
    command: sh -c "sleep 10 && python data_generator.py && uvicorn server:app --host 0.0.0.0 --port 8001"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      REACT_APP_BACKEND_URL: http://localhost:8001
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Step 2: Create Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001
```

### Step 3: Create Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install

COPY . .

EXPOSE 3000

CMD ["yarn", "start"]
```

### Step 4: Deploy
```bash
docker-compose up -d
```

---

## Environment Variables Summary

### Backend (.env)
```bash
POSTGRES_URL="postgresql://user:password@host:5432/database"
CORS_ORIGINS="*"  # Or specific domain
MONGO_URL="mongodb://localhost:27017"  # Optional, for status checks
DB_NAME="test_database"  # Optional, for status checks
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL="https://your-backend-url.com"
WDS_SOCKET_PORT=443  # Optional, for websocket
ENABLE_HEALTH_CHECK=false  # Optional
```

---

## Post-Deployment Steps

### 1. Initialize Database
```bash
# SSH into your server or use platform's console
cd backend
python data_generator.py
```

### 2. Verify Backend
```bash
curl https://your-backend-url.com/api/
# Expected: {"message": "Quick Commerce Analytics API"}
```

### 3. Test Analytics Endpoints
```bash
curl https://your-backend-url.com/api/analytics/overview
# Should return JSON with metrics
```

### 4. Access Frontend
- Open browser to your frontend URL
- Verify all tabs load correctly
- Test Excel export

---

## Troubleshooting

### Issue: Database Connection Failed
**Solution:** 
- Check POSTGRES_URL format: `postgresql://user:password@host:port/database`
- Verify PostgreSQL is running
- Check firewall rules allow connection

### Issue: Frontend Can't Reach Backend
**Solution:**
- Verify REACT_APP_BACKEND_URL is correct
- Check CORS_ORIGINS includes frontend domain
- Ensure backend /api routes are accessible

### Issue: Data Not Loading
**Solution:**
- Run `python data_generator.py` to populate database
- Check backend logs for errors
- Verify database tables exist

### Issue: Excel Export Fails
**Solution:**
- Ensure openpyxl and xlsxwriter are installed
- Check backend has write permissions
- Verify endpoint returns file correctly

---

## Platform Comparison

| Platform | Free Tier | PostgreSQL | Ease | Cost (Small) |
|----------|-----------|------------|------|--------------|
| Heroku | Yes (Dyno hours) | Yes | ⭐⭐⭐⭐⭐ | $7-25/mo |
| Railway | Yes ($5 credit) | Yes | ⭐⭐⭐⭐⭐ | $5-20/mo |
| Render | Yes | Yes | ⭐⭐⭐⭐ | $7-25/mo |
| DigitalOcean | No | Yes | ⭐⭐⭐ | $12-40/mo |
| AWS | Yes (1 year) | Yes | ⭐⭐ | $20-100/mo |
| Docker VPS | Varies | Self-hosted | ⭐⭐⭐ | $5-50/mo |

**Recommended:** Railway or Render for easiest deployment with free tier.

---

## Production Checklist

- [ ] Set secure PostgreSQL password
- [ ] Configure proper CORS_ORIGINS (not "*")
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Configure backups for PostgreSQL
- [ ] Add rate limiting to API
- [ ] Set up CI/CD pipeline
- [ ] Configure environment-specific variables
- [ ] Add health check endpoints
- [ ] Set up logging aggregation

---

## Support

For platform-specific issues:
- **Heroku:** https://devcenter.heroku.com/
- **Railway:** https://docs.railway.app/
- **Render:** https://render.com/docs
- **DigitalOcean:** https://docs.digitalocean.com/
- **AWS:** https://docs.aws.amazon.com/

---

**Note:** The application is fully functional with PostgreSQL and ready for external deployment. Choose the platform that best fits your needs and budget.
