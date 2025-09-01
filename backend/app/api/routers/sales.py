from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database.connection import get_db
from app.schemas.schemas import Sale, SaleCreate
from app.services.crud import sale_service

router = APIRouter()

@router.get("/", response_model=List[Sale])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    customer_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all sales with optional filtering"""
    sales = sale_service.get_sales(
        db=db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        product_id=product_id
    )
    return sales

@router.get("/{sale_id}", response_model=Sale)
async def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get a specific sale by ID"""
    sale = sale_service.get_sale(db=db, sale_id=sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    return sale

@router.post("/", response_model=Sale, status_code=status.HTTP_201_CREATED)
async def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale"""
    try:
        return sale_service.create_sale(db=db, sale=sale)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/customer/{customer_id}", response_model=List[Sale])
async def get_customer_sales(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all sales for a specific customer"""
    sales = sale_service.get_sales_by_customer(
        db=db,
        customer_id=customer_id,
        skip=skip,
        limit=limit
    )
    return sales

@router.get("/product/{product_id}", response_model=List[Sale])
async def get_product_sales(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all sales for a specific product"""
    sales = sale_service.get_sales_by_product(
        db=db,
        product_id=product_id,
        skip=skip,
        limit=limit
    )
    return sales

@router.get("/daily/summary")
async def get_daily_sales_summary(
    date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get daily sales summary"""
    if not date:
        date = datetime.now().date()
    
    summary = sale_service.get_daily_sales_summary(db=db, date=date)
    return summary

@router.get("/weekly/summary")
async def get_weekly_sales_summary(
    week_start: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get weekly sales summary"""
    if not week_start:
        # Start of current week (Monday)
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
    
    summary = sale_service.get_weekly_sales_summary(db=db, week_start=week_start)
    return summary

@router.get("/monthly/summary")
async def get_monthly_sales_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get monthly sales summary"""
    if not year or not month:
        now = datetime.now()
        year = year or now.year
        month = month or now.month
    
    summary = sale_service.get_monthly_sales_summary(db=db, year=year, month=month)
    return summary
