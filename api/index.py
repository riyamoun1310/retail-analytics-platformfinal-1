from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys
import json
from typing import List, Dict, Any

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Initialize FastAPI app with minimal configuration for Vercel
app = FastAPI(
    title="Retail Analytics Platform API",
    description="AI-Powered Retail Analytics Platform for sales prediction and business intelligence",
    version="1.0.0"
)

# Configure CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes for Vercel deployment
@app.get("/")
async def root():
    return {
        "message": "Welcome to Retail Analytics Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "environment": "production"
    }

@app.get("/api")
async def api_root():
    return {
        "message": "Retail Analytics Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("VERCEL_ENV", "development")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

# Sample data endpoints for demo
@app.get("/api/v1/products")
async def get_products():
    """Sample products endpoint"""
    return {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
            {"id": 2, "name": "Smartphone", "price": 599.99, "category": "Electronics"},
            {"id": 3, "name": "Headphones", "price": 199.99, "category": "Audio"}
        ],
        "total": 3
    }

@app.get("/api/v1/sales")
async def get_sales():
    """Sample sales endpoint"""
    return {
        "sales": [
            {"id": 1, "product_id": 1, "quantity": 2, "total": 1999.98, "date": "2024-01-15"},
            {"id": 2, "product_id": 2, "quantity": 1, "total": 599.99, "date": "2024-01-16"},
            {"id": 3, "product_id": 3, "quantity": 3, "total": 599.97, "date": "2024-01-17"}
        ],
        "total": 3
    }

@app.get("/api/v1/analytics/sales-overview")
async def get_sales_overview():
    """Sample analytics endpoint"""
    return {
        "total_revenue": 15675.50,
        "total_orders": 150,
        "average_order_value": 104.50,
        "growth_rate": 12.5,
        "top_products": [
            {"name": "Laptop", "revenue": 5999.95},
            {"name": "Smartphone", "revenue": 4199.93},
            {"name": "Headphones", "revenue": 1999.95}
        ]
    }

@app.post("/api/v1/ml/predict-sales")
async def predict_sales(data: Dict[str, Any] = None):
    """Sample ML prediction endpoint"""
    return {
        "predicted_sales": 2500.75,
        "confidence": 0.87,
        "period": "next_30_days",
        "factors": {
            "seasonality": "high",
            "trend": "increasing",
            "external_factors": "positive"
        }
    }

@app.post("/api/v1/reports/generate")
async def generate_report(data: Dict[str, Any] = None):
    """Sample AI report generation endpoint"""
    return {
        "report": "Based on current sales data, your business is performing well with a 12.5% growth rate. Top performing category is Electronics with $12,199.83 in revenue.",
        "insights": [
            "Electronics category shows strongest performance",
            "Customer acquisition rate is up 15%",
            "Inventory turnover improved by 8%"
        ],
        "recommendations": [
            "Increase electronics inventory by 20%",
            "Focus marketing efforts on high-performing products",
            "Consider expanding electronics product line"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "message": "The requested endpoint does not exist"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "An unexpected error occurred"}

# Vercel handler (required for Vercel deployment)
def handler(event, context):
    return app

# Vercel handler (required for Vercel deployment)
def handler(event, context):
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
