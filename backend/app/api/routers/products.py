from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.database import models
from app.schemas.schemas import Product, ProductCreate, ProductUpdate
from app.services.crud import product_service

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    products = product_service.get_products(
        db=db, 
        skip=skip, 
        limit=limit, 
        category=category, 
        is_active=is_active
    )
    return products

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = product_service.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if SKU already exists
    existing_product = product_service.get_product_by_sku(db=db, sku=product.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    return product_service.create_product(db=db, product=product)

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """Update a product"""
    product = product_service.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product_service.update_product(
        db=db, 
        product_id=product_id, 
        product_update=product_update
    )

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product (soft delete by setting is_active to False)"""
    product = product_service.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product_service.delete_product(db=db, product_id=product_id)
    return {"message": "Product deleted successfully"}

@router.get("/category/{category}", response_model=List[Product])
async def get_products_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get products by category"""
    products = product_service.get_products_by_category(
        db=db, 
        category=category, 
        skip=skip, 
        limit=limit
    )
    return products

@router.get("/low-stock/alert")
async def get_low_stock_products(db: Session = Depends(get_db)):
    """Get products with stock below reorder level"""
    products = product_service.get_low_stock_products(db=db)
    return {
        "count": len(products),
        "products": products
    }
