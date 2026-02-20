from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import models
from app.schemas import schemas
from fastapi import HTTPException
from app.core.security import get_password_hash

# Users
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Customers
def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Products
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Sales Orders
def create_sales_order(db: Session, order: schemas.SalesOrderCreate):
    # Check customer
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    total_amount = 0.0
    db_items = []
    
    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")
        
        # Deduct stock
        product.stock_quantity -= item.quantity
        
        unit_price = product.price
        total_amount += unit_price * item.quantity
        db_items.append(models.OrderItem(product_id=product.id, quantity=item.quantity, unit_price=unit_price))

    db_order = models.SalesOrder(
        customer_id=order.customer_id,
        total_amount=total_amount,
        status=models.OrderStatus.confirmed
    )
    db.add(db_order)
    db.flush() # get order id
    
    for item in db_items:
        item.order_id = db_order.id
        db.add(item)
    
    # Auto-generate invoice
    db_invoice = models.Invoice(order_id=db_order.id, status=models.InvoiceStatus.unpaid)
    db.add(db_invoice)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SalesOrder).offset(skip).limit(limit).all()

# Analytics
def get_dashboard_stats(db: Session):
    total_revenue = db.query(func.sum(models.SalesOrder.total_amount)).filter(models.SalesOrder.status == models.OrderStatus.confirmed).scalar() or 0.0
    total_orders = db.query(func.count(models.SalesOrder.id)).scalar() or 0
    total_customers = db.query(func.count(models.Customer.id)).scalar() or 0
    
    # Top 5 products
    top_products_q = db.query(
        models.Product.name, func.sum(models.OrderItem.quantity).label("total_sold")
    ).join(models.OrderItem, models.Product.id == models.OrderItem.product_id).group_by(models.Product.name).order_by(func.sum(models.OrderItem.quantity).desc()).limit(5).all()
    
    top_products = [{"name": p.name, "sold": p.total_sold} for p in top_products_q]
    
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "top_products": top_products
    }
