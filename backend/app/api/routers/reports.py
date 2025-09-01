from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database.connection import get_db
from app.schemas.schemas import ReportRequest, ReportResponse, ReportType
from app.services.genai_service import GenAIService
from app.services.crud import sale_service, product_service, customer_service

router = APIRouter()
genai_service = GenAIService()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db)
):
    """Generate an AI-powered natural language report"""
    try:
        # Get data based on report type
        data = await get_report_data(db, request)
        
        # Generate report using GenAI
        report = await genai_service.generate_report(request.report_type, data)
        
        return ReportResponse(
            report_type=request.report_type.value,
            summary=report["summary"],
            detailed_analysis=report["detailed_analysis"],
            recommendations=report["recommendations"],
            generated_at=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )

@router.get("/types")
async def get_report_types():
    """Get available report types"""
    return [
        {
            "type": "sales_summary",
            "name": "Sales Summary",
            "description": "Comprehensive overview of sales performance and trends"
        },
        {
            "type": "inventory_status",
            "name": "Inventory Status",
            "description": "Current inventory levels and stock management insights"
        },
        {
            "type": "customer_insights",
            "name": "Customer Insights",
            "description": "Customer behavior analysis and segmentation insights"
        },
        {
            "type": "product_performance",
            "name": "Product Performance",
            "description": "Product sales analysis and performance metrics"
        }
    ]

@router.post("/ask")
async def ask_business_question(
    question: str,
    db: Session = Depends(get_db)
):
    """Ask a natural language question about the business data"""
    try:
        # Get relevant data context
        context = await get_business_context(db)
        
        # Generate answer using GenAI
        answer = await genai_service.answer_question(question, context)
        
        return {
            "question": question,
            "answer": answer,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )

async def get_report_data(db: Session, request: ReportRequest):
    """Get data based on report type and filters"""
    from datetime import timedelta
    
    # Default date range if not provided
    end_date = request.end_date or datetime.now()
    start_date = request.start_date or (end_date - timedelta(days=30))
    
    if request.report_type == ReportType.SALES_SUMMARY:
        return await get_sales_summary_data(db, start_date, end_date)
    
    elif request.report_type == ReportType.INVENTORY_STATUS:
        return await get_inventory_data(db)
    
    elif request.report_type == ReportType.CUSTOMER_INSIGHTS:
        return await get_customer_data(db, start_date, end_date)
    
    elif request.report_type == ReportType.PRODUCT_PERFORMANCE:
        return await get_product_performance_data(db, start_date, end_date)
    
    else:
        raise ValueError(f"Unknown report type: {request.report_type}")

async def get_sales_summary_data(db: Session, start_date: datetime, end_date: datetime):
    """Get sales summary data"""
    from sqlalchemy import func, and_
    from app.database import models
    
    # Total sales metrics
    sales_metrics = db.query(
        func.sum(models.Sale.final_amount).label('total_revenue'),
        func.count(models.Sale.id).label('total_orders'),
        func.avg(models.Sale.final_amount).label('avg_order_value')
    ).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).first()
    
    # Top products
    top_products = db.query(
        models.Product.name,
        func.sum(models.Sale.quantity).label('quantity_sold'),
        func.sum(models.Sale.final_amount).label('revenue')
    ).join(models.Sale).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).group_by(models.Product.id, models.Product.name).order_by(
        func.sum(models.Sale.final_amount).desc()
    ).limit(5).all()
    
    # Sales by category
    category_sales = db.query(
        models.Product.category,
        func.sum(models.Sale.final_amount).label('revenue')
    ).join(models.Sale).filter(
        and_(
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        )
    ).group_by(models.Product.category).all()
    
    return {
        "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        "total_revenue": float(sales_metrics.total_revenue or 0),
        "total_orders": int(sales_metrics.total_orders or 0),
        "avg_order_value": float(sales_metrics.avg_order_value or 0),
        "top_products": [
            {
                "name": product.name,
                "quantity_sold": int(product.quantity_sold),
                "revenue": float(product.revenue)
            }
            for product in top_products
        ],
        "category_sales": [
            {
                "category": category.category,
                "revenue": float(category.revenue)
            }
            for category in category_sales
        ]
    }

async def get_inventory_data(db: Session):
    """Get inventory status data"""
    from sqlalchemy import func
    from app.database import models
    
    # Inventory metrics
    inventory_metrics = db.query(
        func.count(models.Product.id).label('total_products'),
        func.sum(models.Product.stock_quantity).label('total_stock'),
        func.sum(models.Product.stock_quantity * models.Product.cost).label('inventory_value')
    ).filter(models.Product.is_active == True).first()
    
    # Low stock products
    low_stock = db.query(models.Product).filter(
        and_(
            models.Product.stock_quantity <= models.Product.reorder_level,
            models.Product.is_active == True
        )
    ).all()
    
    # Stock by category
    category_stock = db.query(
        models.Product.category,
        func.sum(models.Product.stock_quantity).label('total_stock')
    ).filter(models.Product.is_active == True).group_by(
        models.Product.category
    ).all()
    
    return {
        "total_products": int(inventory_metrics.total_products or 0),
        "total_stock_units": int(inventory_metrics.total_stock or 0),
        "inventory_value": float(inventory_metrics.inventory_value or 0),
        "low_stock_products": [
            {
                "name": product.name,
                "current_stock": product.stock_quantity,
                "reorder_level": product.reorder_level
            }
            for product in low_stock
        ],
        "stock_by_category": [
            {
                "category": category.category,
                "total_stock": int(category.total_stock)
            }
            for category in category_stock
        ]
    }

async def get_customer_data(db: Session, start_date: datetime, end_date: datetime):
    """Get customer insights data"""
    from sqlalchemy import func, and_
    from app.database import models
    
    # Customer metrics
    total_customers = db.query(models.Customer).filter(
        models.Customer.is_active == True
    ).count()
    
    # New customers in period
    new_customers = db.query(models.Customer).filter(
        and_(
            models.Customer.created_at >= start_date,
            models.Customer.created_at <= end_date
        )
    ).count()
    
    # Customer segments
    segments = db.query(
        models.Customer.customer_segment,
        func.count(models.Customer.id).label('count'),
        func.avg(models.Customer.total_spent).label('avg_spent')
    ).filter(models.Customer.is_active == True).group_by(
        models.Customer.customer_segment
    ).all()
    
    # Top customers
    top_customers = db.query(
        models.Customer.first_name,
        models.Customer.last_name,
        models.Customer.total_spent,
        models.Customer.total_orders
    ).filter(models.Customer.is_active == True).order_by(
        models.Customer.total_spent.desc()
    ).limit(5).all()
    
    return {
        "total_customers": total_customers,
        "new_customers": new_customers,
        "customer_segments": [
            {
                "segment": segment.customer_segment or "Unassigned",
                "count": int(segment.count),
                "avg_spent": float(segment.avg_spent or 0)
            }
            for segment in segments
        ],
        "top_customers": [
            {
                "name": f"{customer.first_name} {customer.last_name}",
                "total_spent": float(customer.total_spent),
                "total_orders": int(customer.total_orders)
            }
            for customer in top_customers
        ]
    }

async def get_product_performance_data(db: Session, start_date: datetime, end_date: datetime):
    """Get product performance data"""
    from sqlalchemy import func, and_
    from app.database import models
    
    # Product performance
    product_performance = db.query(
        models.Product.name,
        models.Product.category,
        models.Product.price,
        func.coalesce(func.sum(models.Sale.quantity), 0).label('units_sold'),
        func.coalesce(func.sum(models.Sale.final_amount), 0).label('revenue')
    ).outerjoin(
        models.Sale,
    ).filter(models.Product.is_active == True).group_by(
        models.Product.id, models.Product.name, models.Product.category, models.Product.price
    ).order_by(func.sum(models.Sale.final_amount).desc()).limit(10).all()
    
    return {
        "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        "top_performers": [
            {
                "name": product.name,
                "category": product.category,
                "price": float(product.price),
                "units_sold": int(product.units_sold),
                "revenue": float(product.revenue)
            }
            for product in product_performance
        ]
    }

async def get_business_context(db: Session):
    """Get general business context for answering questions"""
    from datetime import timedelta
    
    # Recent sales summary
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    sales_data = await get_sales_summary_data(db, start_date, end_date)
    inventory_data = await get_inventory_data(db)
    customer_data = await get_customer_data(db, start_date, end_date)
    
    return {
        "recent_sales": sales_data,
        "inventory": inventory_data,
        "customers": customer_data,
        "context_date": datetime.now().isoformat()
    }
