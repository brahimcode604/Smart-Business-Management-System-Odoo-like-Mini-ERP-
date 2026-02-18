from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import enum

# Enums
class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

class OrderStatus(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

class InvoiceStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str
    role: Optional[RoleEnum] = RoleEnum.user

class UserResponse(UserBase):
    id: int
    role: RoleEnum
    class Config:
        from_attributes = True

# Customer
class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Product
class ProductBase(BaseModel):
    name: str
    sku: str
    price: float
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Order Items
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    unit_price: float
    class Config:
        from_attributes = True

# Sales Orders
class SalesOrderBase(BaseModel):
    customer_id: int

class SalesOrderCreate(SalesOrderBase):
    items: List[OrderItemCreate]

class SalesOrderResponse(SalesOrderBase):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse] = []
    class Config:
        from_attributes = True

# Invoice
class InvoiceResponse(BaseModel):
    id: int
    order_id: int
    status: InvoiceStatus
    created_at: datetime
    class Config:
        from_attributes = True
