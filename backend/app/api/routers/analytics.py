from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta
from app.database.connection import get_db
from app.database import models
from app.schemas.schemas import SalesAnalytics

router = APIRouter()

@router.get("/sales-overview", response_model=SalesAnalytics)
async def get_sales_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get comprehensive sales analytics"""
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Base query with date filter
    base_query = db.query(models.Sale).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    )
    
    # Total sales and orders
    sales_summary = base_query.with_entities(
        func.sum(models.Sale.final_amount).label('total_sales'),
        func.count(models.Sale.id).label('total_orders'),
        func.avg(models.Sale.final_amount).label('average_order_value')
    ).first()
    
    # Top products
    top_products = db.query(
        models.Product.name,
        models.Product.category,
        func.sum(models.Sale.quantity).label('total_quantity'),
        func.sum(models.Sale.final_amount).label('total_revenue')
    ).join(models.Sale).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).group_by(
        models.Product.id, models.Product.name, models.Product.category
    ).order_by(
        func.sum(models.Sale.final_amount).desc()
    ).limit(10).all()
    
    # Top customers
    top_customers = db.query(
        models.Customer.first_name,
        models.Customer.last_name,
        models.Customer.email,
        func.sum(models.Sale.final_amount).label('total_spent'),
        func.count(models.Sale.id).label('total_orders')
    ).join(models.Sale).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).group_by(
        models.Customer.id, models.Customer.first_name, 
        models.Customer.last_name, models.Customer.email
    ).order_by(
        func.sum(models.Sale.final_amount).desc()
    ).limit(10).all()
    
    # Sales by category
    sales_by_category = db.query(
        models.Product.category,
        func.sum(models.Sale.final_amount).label('total_revenue'),
        func.sum(models.Sale.quantity).label('total_quantity')
    ).join(models.Sale).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).group_by(models.Product.category).all()
    
    # Sales trend (daily)
    sales_trend = db.query(
        func.date(models.Sale.sale_date).label('date'),
        func.sum(models.Sale.final_amount).label('revenue'),
        func.count(models.Sale.id).label('orders')
    ).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).group_by(func.date(models.Sale.sale_date)).order_by(
        func.date(models.Sale.sale_date)
    ).all()
    
    return SalesAnalytics(
        total_sales=float(sales_summary.total_sales or 0),
        total_orders=int(sales_summary.total_orders or 0),
        average_order_value=float(sales_summary.average_order_value or 0),
        top_products=[
            {
                "name": product.name,
                "category": product.category,
                "total_quantity": int(product.total_quantity),
                "total_revenue": float(product.total_revenue)
            }
            for product in top_products
        ],
        top_customers=[
            {
                "name": f"{customer.first_name} {customer.last_name}",
                "email": customer.email,
                "total_spent": float(customer.total_spent),
                "total_orders": int(customer.total_orders)
            }
            for customer in top_customers
        ],
        sales_by_category=[
            {
                "category": category.category,
                "total_revenue": float(category.total_revenue),
                "total_quantity": int(category.total_quantity)
            }
            for category in sales_by_category
        ],
        sales_trend=[
            {
                "date": trend.date.isoformat(),
                "revenue": float(trend.revenue),
                "orders": int(trend.orders)
            }
            for trend in sales_trend
        ]
    )

@router.get("/inventory-status")
async def get_inventory_status(db: Session = Depends(get_db)):
    """Get current inventory status"""
    
    # Total products
    total_products = db.query(models.Product).filter(
        models.Product.is_active == True
    ).count()
    
    # Low stock products
    low_stock = db.query(models.Product).filter(
        and_(
            models.Product.stock_quantity <= models.Product.reorder_level,
            models.Product.is_active == True
        )
    ).count()
    
    # Out of stock products
    out_of_stock = db.query(models.Product).filter(
        and_(
            models.Product.stock_quantity == 0,
            models.Product.is_active == True
        )
    ).count()
    
    # Inventory value
    inventory_value = db.query(
        func.sum(models.Product.stock_quantity * models.Product.cost).label('total_value')
    ).filter(models.Product.is_active == True).scalar() or 0
    
    return {
        "total_products": total_products,
        "low_stock_products": low_stock,
        "out_of_stock_products": out_of_stock,
        "total_inventory_value": float(inventory_value),
        "stock_health": "Good" if low_stock < total_products * 0.1 else "Warning" if low_stock < total_products * 0.2 else "Critical"
    }

@router.get("/customer-insights")
async def get_customer_insights(db: Session = Depends(get_db)):
    """Get customer analytics and insights"""
    
    # Total customers
    total_customers = db.query(models.Customer).filter(
        models.Customer.is_active == True
    ).count()
    
    # Customer segments
    segments = db.query(
        models.Customer.customer_segment,
        func.count(models.Customer.id).label('count')
    ).filter(models.Customer.is_active == True).group_by(
        models.Customer.customer_segment
    ).all()
    
    # Customer lifetime value
    clv_data = db.query(
        func.avg(models.Customer.total_spent).label('avg_clv'),
        func.max(models.Customer.total_spent).label('max_clv'),
        func.min(models.Customer.total_spent).label('min_clv')
    ).filter(models.Customer.is_active == True).first()
    
    # Recent customer acquisition (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_customers = db.query(models.Customer).filter(
        and_(
            models.Customer.created_at >= thirty_days_ago,
            models.Customer.is_active == True
        )
    ).count()
    
    return {
        "total_customers": total_customers,
        "new_customers_last_30_days": new_customers,
        "customer_segments": [
            {
                "segment": segment.customer_segment or "Unassigned",
                "count": int(segment.count)
            }
            for segment in segments
        ],
        "customer_lifetime_value": {
            "average": float(clv_data.avg_clv or 0),
            "maximum": float(clv_data.max_clv or 0),
            "minimum": float(clv_data.min_clv or 0)
        }
    }

@router.get("/product-performance")
async def get_product_performance(
    category: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get product performance metrics"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Base query
    query = db.query(
        models.Product.name,
        models.Product.category,
        models.Product.brand,
        models.Product.price,
        models.Product.stock_quantity,
        func.coalesce(func.sum(models.Sale.quantity), 0).label('units_sold'),
        func.coalesce(func.sum(models.Sale.final_amount), 0).label('revenue'),
        func.count(models.Sale.id).label('transaction_count')
    ).outerjoin(
        models.Sale,
        and_(
            models.Sale.product_id == models.Product.id,
            models.Sale.sale_date >= start_date
        )
    ).filter(models.Product.is_active == True)
    
    if category:
        query = query.filter(models.Product.category == category)
    
    products = query.group_by(
        models.Product.id, models.Product.name, models.Product.category,
        models.Product.brand, models.Product.price, models.Product.stock_quantity
    ).order_by(func.sum(models.Sale.final_amount).desc()).all()
    
    return {
        "analysis_period_days": days,
        "category_filter": category,
        "products": [
            {
                "name": product.name,
                "category": product.category,
                "brand": product.brand,
                "price": float(product.price),
                "current_stock": int(product.stock_quantity),
                "units_sold": int(product.units_sold),
                "revenue": float(product.revenue),
                "transaction_count": int(product.transaction_count),
                "revenue_per_unit": float(product.revenue / product.units_sold) if product.units_sold > 0 else 0
            }
            for product in products
        ]
    }
