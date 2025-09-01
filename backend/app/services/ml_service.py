import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from app.database import models
from app.schemas.schemas import PredictionResponse
from app.core.config import settings

class MLService:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model_version = "1.0.0"
        self.last_trained = None
        self.model_path = settings.MODEL_PATH
        self.load_model()
    
    def load_model(self):
        """Load the trained model if it exists"""
        try:
            if os.path.exists(os.path.join(self.model_path, "sales_model.pkl")):
                self.model = joblib.load(os.path.join(self.model_path, "sales_model.pkl"))
                self.scaler = joblib.load(os.path.join(self.model_path, "scaler.pkl"))
                self.label_encoders = joblib.load(os.path.join(self.model_path, "label_encoders.pkl"))
                
                # Load metadata
                if os.path.exists(os.path.join(self.model_path, "model_metadata.pkl")):
                    metadata = joblib.load(os.path.join(self.model_path, "model_metadata.pkl"))
                    self.model_version = metadata.get("version", "1.0.0")
                    self.last_trained = metadata.get("last_trained")
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            self.model = None
    
    def save_model(self):
        """Save the trained model"""
        os.makedirs(self.model_path, exist_ok=True)
        
        joblib.dump(self.model, os.path.join(self.model_path, "sales_model.pkl"))
        joblib.dump(self.scaler, os.path.join(self.model_path, "scaler.pkl"))
        joblib.dump(self.label_encoders, os.path.join(self.model_path, "label_encoders.pkl"))
        
        # Save metadata
        metadata = {
            "version": self.model_version,
            "last_trained": datetime.now(),
            "features": self.get_feature_names()
        }
        joblib.dump(metadata, os.path.join(self.model_path, "model_metadata.pkl"))
    
    def prepare_features(self, db: Session, product_id: int = None) -> pd.DataFrame:
        """Prepare features for training or prediction"""
        # Base query for sales data with product and customer information
        query = db.query(
            models.Sale.product_id,
            models.Sale.quantity,
            models.Sale.unit_price,
            models.Sale.final_amount,
            models.Sale.sale_date,
            models.Sale.sales_channel,
            models.Sale.store_location,
            models.Product.category,
            models.Product.brand,
            models.Product.price,
            models.Customer.customer_segment,
            models.Customer.city
        ).join(models.Product).join(models.Customer)
        
        if product_id:
            query = query.filter(models.Sale.product_id == product_id)
        
        # Get sales data from last 2 years
        two_years_ago = datetime.now() - timedelta(days=730)
        sales_data = query.filter(models.Sale.sale_date >= two_years_ago).all()
        
        if not sales_data:
            raise ValueError("No sales data available for feature preparation")
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'product_id': sale.product_id,
                'quantity': sale.quantity,
                'unit_price': sale.unit_price,
                'final_amount': sale.final_amount,
                'sale_date': sale.sale_date,
                'sales_channel': sale.sales_channel,
                'store_location': sale.store_location or 'Unknown',
                'category': sale.category,
                'brand': sale.brand or 'Unknown',
                'price': sale.price,
                'customer_segment': sale.customer_segment or 'Unknown',
                'city': sale.city or 'Unknown'
            }
            for sale in sales_data
        ])
        
        # Feature engineering
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['month'] = df['sale_date'].dt.month
        df['quarter'] = df['sale_date'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Aggregate daily sales by product
        daily_sales = df.groupby(['product_id', df['sale_date'].dt.date]).agg({
            'quantity': 'sum',
            'final_amount': 'sum',
            'unit_price': 'mean',
            'price': 'first',
            'category': 'first',
            'brand': 'first',
            'day_of_week': 'first',
            'month': 'first',
            'quarter': 'first',
            'is_weekend': 'first'
        }).reset_index()
        
        # Add historical features (rolling averages)
        daily_sales = daily_sales.sort_values(['product_id', 'sale_date'])
        daily_sales['quantity_7d_avg'] = daily_sales.groupby('product_id')['quantity'].rolling(7, min_periods=1).mean().reset_index(drop=True)
        daily_sales['quantity_30d_avg'] = daily_sales.groupby('product_id')['quantity'].rolling(30, min_periods=1).mean().reset_index(drop=True)
        
        return daily_sales
    
    def encode_categorical_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Encode categorical features"""
        categorical_columns = ['category', 'brand', 'sales_channel', 'store_location', 'customer_segment', 'city']
        
        for col in categorical_columns:
            if col in df.columns:
                if fit:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    if col in self.label_encoders:
                        # Handle unseen categories
                        df[f'{col}_encoded'] = df[col].astype(str).apply(
                            lambda x: self.label_encoders[col].transform([x])[0] 
                            if x in self.label_encoders[col].classes_ else -1
                        )
                    else:
                        df[f'{col}_encoded'] = 0
        
        return df
    
    def train_model(self, db: Session):
        """Train the sales prediction model"""
        # Prepare features
        df = self.prepare_features(db)
        
        # Encode categorical features
        df = self.encode_categorical_features(df, fit=True)
        
        # Select features for training
        feature_columns = [
            'unit_price', 'price', 'day_of_week', 'month', 'quarter', 'is_weekend',
            'quantity_7d_avg', 'quantity_30d_avg', 'category_encoded', 'brand_encoded'
        ]
        
        # Filter valid rows
        df = df.dropna(subset=feature_columns + ['quantity'])
        
        if len(df) < 50:
            raise ValueError("Insufficient data for training (minimum 50 samples required)")
        
        X = df[feature_columns]
        y = df['quantity']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        
        # Update metadata
        self.last_trained = datetime.now()
        self.model_version = f"1.0.{int(datetime.now().timestamp())}"
        
        # Save model
        self.save_model()
        
        # Return training metrics
        y_pred = self.model.predict(X_test)
        return {
            "mae": mean_absolute_error(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }
    
    def predict_sales(self, db: Session, product_id: int, days_ahead: int = 7) -> PredictionResponse:
        """Predict sales for a specific product"""
        if not self.model:
            # Train model if not available
            print("No model found, training new model...")
            self.train_model(db)
        
        # Get product information
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Get recent sales data for the product
        recent_sales = db.query(models.Sale).filter(
            models.Sale.product_id == product_id,
            models.Sale.sale_date >= datetime.now() - timedelta(days=90)
        ).all()
        
        if not recent_sales:
            # Use average sales if no recent data
            predicted_quantity = 1.0
            confidence_score = 0.3
        else:
            # Prepare features for prediction
            df = self.prepare_features(db, product_id)
            
            if df.empty:
                predicted_quantity = 1.0
                confidence_score = 0.3
            else:
                # Use latest data point for prediction
                df = self.encode_categorical_features(df, fit=False)
                latest_data = df.iloc[-1:].copy()
                
                # Prepare prediction date features
                prediction_date = datetime.now() + timedelta(days=days_ahead)
                latest_data['day_of_week'] = prediction_date.weekday()
                latest_data['month'] = prediction_date.month
                latest_data['quarter'] = (prediction_date.month - 1) // 3 + 1
                latest_data['is_weekend'] = int(prediction_date.weekday() in [5, 6])
                
                feature_columns = [
                    'unit_price', 'price', 'day_of_week', 'month', 'quarter', 'is_weekend',
                    'quantity_7d_avg', 'quantity_30d_avg', 'category_encoded', 'brand_encoded'
                ]
                
                X = latest_data[feature_columns].fillna(0)
                X_scaled = self.scaler.transform(X)
                
                predicted_quantity = float(self.model.predict(X_scaled)[0])
                
                # Calculate confidence based on model's feature importance and data recency
                confidence_score = min(0.95, max(0.1, 0.8 - (days_ahead * 0.05)))
        
        return PredictionResponse(
            product_id=product_id,
            product_name=product.name,
            predicted_quantity=max(0, predicted_quantity),
            confidence_score=confidence_score,
            prediction_date=datetime.now() + timedelta(days=days_ahead),
            model_version=self.model_version
        )
    
    def retrain_model(self, db: Session):
        """Retrain the model with latest data"""
        try:
            metrics = self.train_model(db)
            print(f"Model retrained successfully. Metrics: {metrics}")
            return metrics
        except Exception as e:
            print(f"Model retraining failed: {str(e)}")
            raise e
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_type": "RandomForestRegressor",
            "version": self.model_version,
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
            "is_trained": self.model is not None,
            "features": self.get_feature_names()
        }
    
    def get_feature_names(self) -> List[str]:
        """Get feature names used by the model"""
        return [
            'unit_price', 'price', 'day_of_week', 'month', 'quarter', 'is_weekend',
            'quantity_7d_avg', 'quantity_30d_avg', 'category_encoded', 'brand_encoded'
        ]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model"""
        if not self.model:
            raise ValueError("Model not trained")
        
        feature_names = self.get_feature_names()
        importances = self.model.feature_importances_
        
        return {
            name: float(importance) 
            for name, importance in zip(feature_names, importances)
        }
    
    def evaluate_model(self, db: Session) -> Dict[str, float]:
        """Evaluate model performance on recent data"""
        if not self.model:
            raise ValueError("Model not trained")
        
        # Get recent data for evaluation
        df = self.prepare_features(db)
        df = self.encode_categorical_features(df, fit=False)
        
        # Use last 30 days as test set
        cutoff_date = datetime.now() - timedelta(days=30)
        test_df = df[pd.to_datetime(df['sale_date']) >= cutoff_date]
        
        if test_df.empty:
            raise ValueError("No recent data available for evaluation")
        
        feature_columns = self.get_feature_names()
        X_test = test_df[feature_columns].fillna(0)
        y_test = test_df['quantity']
        
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)
        
        return {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "mse": float(mean_squared_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "samples": len(y_test)
        }
    
    def optimize_inventory(self, db: Session, product_id: int) -> Dict[str, Any]:
        """Get inventory optimization recommendations"""
        # Get product info
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Get sales predictions for next 30 days
        predictions = []
        for days in range(1, 31):
            pred = self.predict_sales(db, product_id, days)
            predictions.append(pred.predicted_quantity)
        
        # Calculate recommendations
        total_predicted_demand = sum(predictions)
        current_stock = product.stock_quantity
        reorder_level = product.reorder_level
        
        # Calculate optimal stock levels
        safety_stock = max(reorder_level, total_predicted_demand * 0.1)
        optimal_stock = total_predicted_demand + safety_stock
        
        recommendations = []
        if current_stock < total_predicted_demand:
            recommendations.append(f"Urgent reorder needed: predicted demand ({total_predicted_demand:.1f}) exceeds current stock ({current_stock})")
        
        if current_stock < safety_stock:
            recommendations.append(f"Stock below safety level: increase to {safety_stock:.1f} units")
        
        if current_stock > optimal_stock * 2:
            recommendations.append(f"Overstock detected: consider reducing orders or promotions")
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "current_stock": current_stock,
            "predicted_30_day_demand": total_predicted_demand,
            "recommended_stock_level": optimal_stock,
            "safety_stock": safety_stock,
            "days_of_stock_remaining": current_stock / (total_predicted_demand / 30) if total_predicted_demand > 0 else float('inf'),
            "recommendations": recommendations,
            "status": "critical" if current_stock < total_predicted_demand * 0.5 else "warning" if current_stock < total_predicted_demand else "good"
        }
