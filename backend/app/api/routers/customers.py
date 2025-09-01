from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.schemas.schemas import Customer, CustomerCreate, CustomerUpdate
from app.services.crud import customer_service

router = APIRouter()

@router.get("/", response_model=List[Customer])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_segment: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all customers with optional filtering"""
    customers = customer_service.get_customers(
        db=db,
        skip=skip,
        limit=limit,
        customer_segment=customer_segment,
        is_active=is_active
    )
    return customers

@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer by ID"""
    customer = customer_service.get_customer(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if email already exists
    existing_customer = customer_service.get_customer_by_email(db=db, email=customer.email)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists"
        )
    
    return customer_service.create_customer(db=db, customer=customer)

@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """Update a customer"""
    customer = customer_service.get_customer(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer_service.update_customer(
        db=db,
        customer_id=customer_id,
        customer_update=customer_update
    )

@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer (soft delete by setting is_active to False)"""
    customer = customer_service.get_customer(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer_service.delete_customer(db=db, customer_id=customer_id)
    return {"message": "Customer deleted successfully"}

@router.get("/{customer_id}/stats")
async def get_customer_stats(customer_id: int, db: Session = Depends(get_db)):
    """Get customer statistics"""
    customer = customer_service.get_customer(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    stats = customer_service.get_customer_stats(db=db, customer_id=customer_id)
    return stats

@router.get("/segment/{segment}", response_model=List[Customer])
async def get_customers_by_segment(
    segment: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get customers by segment"""
    customers = customer_service.get_customers_by_segment(
        db=db,
        segment=segment,
        skip=skip,
        limit=limit
    )
    return customers
