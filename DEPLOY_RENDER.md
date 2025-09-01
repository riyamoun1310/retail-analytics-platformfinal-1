# Render Deployment Guide

## 🚀 Deploy to Render

### Option 1: One-Click Deploy (Recommended)

1. **Fork this repository** to your GitHub account

2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Sign up/Login with your GitHub account
   - Click "New +" → "Blueprint"
   - Connect your forked repository
   - Render will automatically deploy using `render.yaml`

### Option 2: Manual Setup

#### Step 1: Deploy Database
1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Name: `retail-analytics-db`
4. Database Name: `retail_analytics`
5. User: `retail_user`
6. Region: Choose closest to you
7. Plan: Free
8. Click "Create Database"

#### Step 2: Deploy Backend
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `retail-analytics-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Environment Variables**:
   ```
   DATABASE_URL=<Copy from your PostgreSQL service>
   SECRET_KEY=<Generate a secure random string>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   DEBUG=False
   ALLOWED_ORIGINS=["https://your-frontend-url.onrender.com"]
   MODEL_PATH=./models/
   RETRAIN_INTERVAL_HOURS=24
   OPENAI_API_KEY=<Your OpenAI API Key (optional)>
   ```

#### Step 3: Deploy Frontend
1. Click "New +" → "Web Service"
2. Connect the same repository
3. Configure:
   - **Name**: `retail-analytics-frontend`
   - **Root Directory**: `frontend`
   - **Environment**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Environment Variables**:
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com
   ```

### Step 4: Update CORS Settings
After frontend deployment, update the backend's `ALLOWED_ORIGINS` environment variable with your actual frontend URL.

## 🔧 Production Configuration

### Backend Optimizations
- Uses Gunicorn for production WSGI server
- Database connection pooling enabled
- Automatic SSL redirect
- Environment-based configuration

### Frontend Optimizations
- Vite production build
- Asset optimization
- CDN-ready static files
- Environment-based API URLs

## 🎯 Expected URLs
- **Frontend**: `https://retail-analytics-frontend.onrender.com`
- **Backend API**: `https://retail-analytics-backend.onrender.com`
- **API Docs**: `https://retail-analytics-backend.onrender.com/docs`

## ⚠️ Important Notes

1. **Free Tier Limitations**:
   - Services sleep after 15 minutes of inactivity
   - First request after sleep takes ~30 seconds
   - 750 hours/month limit per service

2. **Database**:
   - Free PostgreSQL has 1GB storage limit
   - No automated backups on free tier

3. **Environment Variables**:
   - Never commit real API keys to Git
   - Use Render's environment variable system
   - Update CORS origins after deployment

## 🔒 Security Checklist
- [ ] Use strong SECRET_KEY
- [ ] Set DEBUG=False for production
- [ ] Configure proper CORS origins
- [ ] Use HTTPS URLs only
- [ ] Secure database credentials

## 🚀 Post-Deployment
1. Test all API endpoints
2. Verify database connection
3. Check frontend-backend communication
4. Test ML predictions
5. Verify AI report generation (if OpenAI key provided)

## 📱 Monitoring
- Use Render's built-in logs and metrics
- Monitor service health from dashboard
- Set up alerts for service failures
