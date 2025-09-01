from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
from app.database import models
from app.schemas import schemas

class ProductService:
    def get_product(self, db: Session, product_id: int):
        return db.query(models.Product).filter(models.Product.id == product_id).first()
    
    def get_product_by_sku(self, db: Session, sku: str):
        return db.query(models.Product).filter(models.Product.sku == sku).first()
    
    def get_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ):
        query = db.query(models.Product)
        
        if category:
            query = query.filter(models.Product.category == category)
        if is_active is not None:
            query = query.filter(models.Product.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()
    
    def get_products_by_category(
        self, 
        db: Session, 
        category: str, 
        skip: int = 0, 
        limit: int = 100
    ):
        return db.query(models.Product).filter(
            models.Product.category == category,
            models.Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_low_stock_products(self, db: Session):
        return db.query(models.Product).filter(
            models.Product.stock_quantity <= models.Product.reorder_level,
            models.Product.is_active == True
        ).all()
    
    def create_product(self, db: Session, product: schemas.ProductCreate):
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    def update_product(
        self, 
        db: Session, 
        product_id: int, 
        product_update: schemas.ProductUpdate
    ):
        db_product = self.get_product(db, product_id)
        if db_product:
            update_data = product_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_product, field, value)
            db.commit()
            db.refresh(db_product)
        return db_product
    
    def delete_product(self, db: Session, product_id: int):
        db_product = self.get_product(db, product_id)
        if db_product:
            db_product.is_active = False
            db.commit()
        return db_product

class CustomerService:
    def get_customer(self, db: Session, customer_id: int):
        return db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    
    def get_customer_by_email(self, db: Session, email: str):
        return db.query(models.Customer).filter(models.Customer.email == email).first()
    
    def get_customers(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        customer_segment: Optional[str] = None,
        is_active: Optional[bool] = None
    ):
        query = db.query(models.Customer)
        
        if customer_segment:
            query = query.filter(models.Customer.customer_segment == customer_segment)
        if is_active is not None:
            query = query.filter(models.Customer.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()
    
    def get_customers_by_segment(
        self, 
        db: Session, 
        segment: str, 
        skip: int = 0, 
        limit: int = 100
    ):
        return db.query(models.Customer).filter(
            models.Customer.customer_segment == segment,
            models.Customer.is_active == True
        ).offset(skip).limit(limit).all()
    
    def create_customer(self, db: Session, customer: schemas.CustomerCreate):
        db_customer = models.Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    def update_customer(
        self, 
        db: Session, 
        customer_id: int, 
        customer_update: schemas.CustomerUpdate
    ):
        db_customer = self.get_customer(db, customer_id)
        if db_customer:
            update_data = customer_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_customer, field, value)
            db.commit()
            db.refresh(db_customer)
        return db_customer
    
    def delete_customer(self, db: Session, customer_id: int):
        db_customer = self.get_customer(db, customer_id)
        if db_customer:
            db_customer.is_active = False
            db.commit()
        return db_customer
    
    def get_customer_stats(self, db: Session, customer_id: int):
        # Get customer sales statistics
        sales_stats = db.query(
            func.sum(models.Sale.final_amount).label('total_spent'),
            func.count(models.Sale.id).label('total_orders'),
            func.avg(models.Sale.final_amount).label('avg_order_value')
        ).filter(models.Sale.customer_id == customer_id).first()
        
        return {
            "total_spent": float(sales_stats.total_spent or 0),
            "total_orders": int(sales_stats.total_orders or 0),
            "avg_order_value": float(sales_stats.avg_order_value or 0)
        }

class SaleService:
    def get_sale(self, db: Session, sale_id: int):
        return db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    
    def get_sales(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        customer_id: Optional[int] = None,
        product_id: Optional[int] = None
    ):
        query = db.query(models.Sale)
        
        if start_date:
            query = query.filter(models.Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(models.Sale.sale_date <= end_date)
        if customer_id:
            query = query.filter(models.Sale.customer_id == customer_id)
        if product_id:
            query = query.filter(models.Sale.product_id == product_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_sales_by_customer(
        self, 
        db: Session, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ):
        return db.query(models.Sale).filter(
            models.Sale.customer_id == customer_id
        ).offset(skip).limit(limit).all()
    
    def get_sales_by_product(
        self, 
        db: Session, 
        product_id: int, 
        skip: int = 0, 
        limit: int = 100
    ):
        return db.query(models.Sale).filter(
            models.Sale.product_id == product_id
        ).offset(skip).limit(limit).all()
    
    def create_sale(self, db: Session, sale: schemas.SaleCreate):
        # Calculate totals
        total_amount = sale.quantity * sale.unit_price
        final_amount = total_amount - sale.discount_amount + sale.tax_amount
        
        # Validate product and customer exist
        product = db.query(models.Product).filter(models.Product.id == sale.product_id).first()
        if not product:
            raise ValueError("Product not found")
            
        customer = db.query(models.Customer).filter(models.Customer.id == sale.customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        # Check stock availability
        if product.stock_quantity < sale.quantity:
            raise ValueError("Insufficient stock")
        
        # Create sale
        db_sale = models.Sale(
            **sale.dict(),
            total_amount=total_amount,
            final_amount=final_amount
        )
        db.add(db_sale)
        
        # Update product stock
        product.stock_quantity -= sale.quantity
        
        # Update customer totals
        customer.total_spent += final_amount
        customer.total_orders += 1
        
        db.commit()
        db.refresh(db_sale)
        return db_sale
    
    def get_daily_sales_summary(self, db: Session, date: datetime):
        sales_data = db.query(
            func.sum(models.Sale.final_amount).label('total_revenue'),
            func.count(models.Sale.id).label('total_orders'),
            func.avg(models.Sale.final_amount).label('avg_order_value')
        ).filter(
            func.date(models.Sale.sale_date) == date
        ).first()
        
        return {
            "date": date.isoformat(),
            "total_revenue": float(sales_data.total_revenue or 0),
            "total_orders": int(sales_data.total_orders or 0),
            "avg_order_value": float(sales_data.avg_order_value or 0)
        }
    
    def get_weekly_sales_summary(self, db: Session, week_start: datetime):
        from datetime import timedelta
        week_end = week_start + timedelta(days=7)
        
        sales_data = db.query(
            func.sum(models.Sale.final_amount).label('total_revenue'),
            func.count(models.Sale.id).label('total_orders'),
            func.avg(models.Sale.final_amount).label('avg_order_value')
        ).filter(
            and_(
                models.Sale.sale_date >= week_start,
                models.Sale.sale_date < week_end
            )
        ).first()
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_revenue": float(sales_data.total_revenue or 0),
            "total_orders": int(sales_data.total_orders or 0),
            "avg_order_value": float(sales_data.avg_order_value or 0)
        }
    
    def get_monthly_sales_summary(self, db: Session, year: int, month: int):
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        sales_data = db.query(
            func.sum(models.Sale.final_amount).label('total_revenue'),
            func.count(models.Sale.id).label('total_orders'),
            func.avg(models.Sale.final_amount).label('avg_order_value')
        ).filter(
            and_(
                models.Sale.sale_date >= start_date,
                models.Sale.sale_date < end_date
            )
        ).first()
        
        return {
            "year": year,
            "month": month,
            "total_revenue": float(sales_data.total_revenue or 0),
            "total_orders": int(sales_data.total_orders or 0),
            "avg_order_value": float(sales_data.avg_order_value or 0)
        }

# Create service instances
product_service = ProductService()
customer_service = CustomerService()
sale_service = SaleService()
