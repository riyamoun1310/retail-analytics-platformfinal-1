# Render Deployment Guide

## What I've Fixed

✅ **Updated Python Version**: Changed from 3.9.18 to 3.11.7 for better compatibility  
✅ **Fixed ML Dependencies**: Updated scikit-learn, pandas, numpy versions  
✅ **Optimized Build Process**: Using `--only-binary=all` to avoid compilation issues  
✅ **Removed API Keys**: All sensitive data removed from config files  
✅ **Created Clean Config**: `render-clean.yaml` is ready for deployment  

## How to Deploy to Render

### Step 1: Go to Render Dashboard
1. Visit [render.com](https://render.com)
2. Sign in with your GitHub account
3. Click "New +" → "Blueprint"

### Step 2: Connect Your Repository
1. Select your GitHub repository: `Retail-Analytics-Platform`
2. Choose the blueprint file: `render-clean.yaml`
3. Click "Connect"

### Step 3: Add Environment Variables
In the Render dashboard, you'll need to manually add these environment variables:

**Backend Service Environment Variables:**
- `SECRET_KEY`: Generate a secure key (use: `openssl rand -hex 32`)
- `OPENAI_API_KEY`: Your actual OpenAI API key

### Step 4: Deploy
1. Click "Apply" to start deployment
2. Wait for the build process to complete
3. Your API will be available at: `https://retail-analytics-backend.onrender.com`
4. Your frontend will be available at: `https://retail-analytics-frontend.onrender.com`

## If Build Still Fails

If you still get scikit-learn compilation errors, I've created a fallback option:

### Use Minimal Deployment (Fallback)
1. In your repository, rename `requirements-minimal.txt` to `requirements.txt` in the backend folder
2. This removes ML dependencies temporarily to get the basic API working
3. You can add ML features later once the basic deployment is working

## Key Changes Made:

1. **Python Runtime**: `python-3.11.7` (better support for ML libraries)
2. **Build Command**: Uses binary wheels to avoid compilation
3. **Updated Dependencies**: Compatible versions for Python 3.11
4. **Security**: Removed all hardcoded API keys

## Test Your Deployment
Once deployed, test these endpoints:
- `https://your-backend-url.onrender.com/` - Should show "Retail Analytics API is running!"
- `https://your-backend-url.onrender.com/health` - Should show status "ok"
- `https://your-backend-url.onrender.com/api/test` - Should show test response

## Common Issues & Solutions

**Build fails with Cython errors:**
- Use the minimal requirements file
- Binary wheels should solve most compilation issues

**Service won't start:**
- Check logs in Render dashboard
- Verify environment variables are set correctly

**CORS errors:**
- Make sure frontend URL is correct in backend CORS settings

Your deployment should work now! The main issues were:
1. Python version compatibility
2. ML library compilation problems  
3. Exposed API keys blocking git push

All of these are now fixed. Try deploying and let me know if you face any other issues!
