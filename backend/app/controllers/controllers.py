from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.db.database import get_db
from app.schemas import schemas
from app.services import services
from app.core import security, dependencies
from app.core.config import settings

router = APIRouter()

# Auth
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: dict = Depends()):
    # Here we expect JSON containing username and password just to be simpler for API
    # But usually OAuth2 expects form data. We will use a regular model if needed.
    # To conform to FastAPI OAuth2PasswordRequestForm, we should use it.
    pass

from fastapi.security import OAuth2PasswordRequestForm
@router.post("/token/form", response_model=schemas.Token)
def login_swagger(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = services.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/api/login", response_model=schemas.Token)
def login_api(user_login: schemas.UserCreate, db: Session = Depends(get_db)):
    user = services.get_user_by_username(db, username=user_login.username)
    if not user or not security.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(dependencies.get_current_user)):
    return current_user

# Customers
@router.get("/api/customers", response_model=List[schemas.CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_user)):
    return services.get_customers(db, skip=skip, limit=limit)

@router.post("/api/customers", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_user)):
    return services.create_customer(db=db, customer=customer)

# Products
@router.get("/api/products", response_model=List[schemas.ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_user)):
    return services.get_products(db, skip=skip, limit=limit)

@router.post("/api/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_admin)):
    return services.create_product(db=db, product=product)

# Sales
@router.get("/api/sales", response_model=List[schemas.SalesOrderResponse])
def get_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_user)):
    return services.get_orders(db, skip=skip, limit=limit)

@router.post("/api/sales", response_model=schemas.SalesOrderResponse)
def create_sale(order: schemas.SalesOrderCreate, db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_user)):
    return services.create_sales_order(db=db, order=order)

# Analytics
@router.get("/api/analytics/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user = Depends(dependencies.get_current_user)):
    return services.get_dashboard_stats(db)
