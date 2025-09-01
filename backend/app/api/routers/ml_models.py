from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database.connection import get_db
from app.schemas.schemas import PredictionRequest, PredictionResponse
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

@router.post("/predict-sales", response_model=PredictionResponse)
async def predict_sales(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """Predict future sales for a specific product"""
    try:
        prediction = ml_service.predict_sales(
            db=db,
            product_id=request.product_id,
            days_ahead=request.days_ahead
        )
        return prediction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@router.post("/predict-sales/batch", response_model=List[PredictionResponse])
async def predict_sales_batch(
    requests: List[PredictionRequest],
    db: Session = Depends(get_db)
):
    """Predict sales for multiple products"""
    predictions = []
    for request in requests:
        try:
            prediction = ml_service.predict_sales(
                db=db,
                product_id=request.product_id,
                days_ahead=request.days_ahead
            )
            predictions.append(prediction)
        except Exception as e:
            # Log error but continue with other predictions
            print(f"Failed to predict for product {request.product_id}: {str(e)}")
            continue
    
    return predictions

@router.post("/retrain-model")
async def retrain_model(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Retrain the sales prediction model with latest data"""
    background_tasks.add_task(ml_service.retrain_model, db)
    return {
        "message": "Model retraining started in background",
        "status": "in_progress"
    }

@router.get("/model-info")
async def get_model_info():
    """Get information about the current ML model"""
    info = ml_service.get_model_info()
    return info

@router.get("/model-performance")
async def get_model_performance(db: Session = Depends(get_db)):
    """Get model performance metrics"""
    try:
        performance = ml_service.evaluate_model(db)
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate model: {str(e)}"
        )

@router.get("/feature-importance")
async def get_feature_importance():
    """Get feature importance from the current model"""
    try:
        importance = ml_service.get_feature_importance()
        return importance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature importance: {str(e)}"
        )

@router.post("/optimize-inventory/{product_id}")
async def optimize_inventory(product_id: int, db: Session = Depends(get_db)):
    """Get inventory optimization recommendations for a product"""
    try:
        recommendations = ml_service.optimize_inventory(db, product_id)
        return recommendations
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inventory optimization failed: {str(e)}"
        )
