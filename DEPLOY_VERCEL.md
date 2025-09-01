# Vercel Deployment Guide

## Prerequisites
1. GitHub account
2. Vercel account (free tier available)
3. Push your code to a GitHub repository

## Step-by-Step Deployment

### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign in with your GitHub account
3. Click "New Project"
4. Import your `Retail-Analytics-Platform` repository

### 3. Configure Build Settings
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 4. Environment Variables
Add these environment variables in Vercel dashboard:

#### Required Variables:
```
SECRET_KEY=your-secret-key-change-this
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=sqlite:///./retail_analytics.db
ENVIRONMENT=production
DEBUG=false
```

#### Optional Variables (for PostgreSQL):
```
DATABASE_URL=postgresql://user:password@host:port/database
```

### 5. Domain Configuration
After deployment:
1. Note your Vercel app URL (e.g., `https://your-app.vercel.app`)
2. Update the frontend environment variable:
   - `VITE_API_BASE_URL=https://your-app.vercel.app`

### 6. Deploy
1. Click "Deploy"
2. Wait for the build to complete
3. Your app will be available at the provided URL

## Project Structure for Vercel

```
/
├── api/
│   └── index.py          # Serverless function entry point
├── frontend/
│   ├── src/
│   ├── dist/            # Build output (auto-generated)
│   └── package.json
├── backend/
│   ├── app/
│   └── requirements.txt
├── vercel.json          # Vercel configuration
└── README.md
```

## API Endpoints
After deployment, your API will be available at:
- Main API: `https://your-app.vercel.app/api/v1/`
- Documentation: `https://your-app.vercel.app/docs`
- Health Check: `https://your-app.vercel.app/health`

## Troubleshooting

### Common Issues:

1. **Python 3.12 `distutils` Error** ✅ FIXED
   ```
   ModuleNotFoundError: No module named 'distutils'
   ```
   **Solution**: Updated to use Python 3.9 runtime and compatible package versions

2. **Build Failures**
   - Check that all dependencies are in `api/requirements.txt`
   - Ensure Node.js version compatibility
   - Verify Python runtime is set to 3.9

3. **API Timeout**
   - Vercel serverless functions have a 10-second timeout on hobby plan
   - Consider upgrading for longer timeouts

4. **Database Issues**
   - SQLite is ephemeral on Vercel (resets on each deployment)
   - Consider using PostgreSQL with a service like Supabase or Neon

5. **CORS Errors**
   - Ensure your domain is in the ALLOWED_ORIGINS list
   - Check that API endpoints are correctly configured

### Recommended Database Solutions:
1. **Supabase** (PostgreSQL) - Free tier available
2. **PlanetScale** (MySQL) - Free tier available
3. **Neon** (PostgreSQL) - Free tier available

## Performance Optimization

1. **Frontend**:
   - Enable gzip compression
   - Optimize bundle size
   - Use code splitting

2. **Backend**:
   - Implement caching
   - Optimize database queries
   - Use connection pooling

## Security Considerations

1. Never commit sensitive data to Git
2. Use environment variables for all secrets
3. Enable HTTPS (automatic with Vercel)
4. Implement rate limiting
5. Validate all inputs

## Monitoring

Vercel provides:
- Function logs
- Performance metrics
- Error tracking
- Analytics

Access these through your Vercel dashboard.

## Scaling

For production use, consider:
- Upgrading to Vercel Pro for better performance
- Using a dedicated database service
- Implementing Redis for caching
- Adding monitoring and logging services
