from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

# Import routers
from app.api.routers import products, sales, customers, analytics, reports
# from app.api.routers import ml_models  # Disabled for initial deployment
from app.database.connection import get_db, engine
from app.database import models
from app.core.config import settings
import os

# Create database tables with error handling
try:
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Database initialization error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Retail Analytics API...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Tavily API Key configured: {'Yes' if settings.TAVILY_API_KEY else 'No'}")
    yield
    # Shutdown
    print("Shutting down Retail Analytics API...")

# Initialize FastAPI app
app = FastAPI(
    title="Retail Analytics Platform API",
    description="AI-Powered Retail Analytics Platform for sales prediction and business intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["sales"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
# app.include_router(ml_models.router, prefix="/api/v1/ml", tags=["machine-learning"])  # Disabled
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Retail Analytics Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
