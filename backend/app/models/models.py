from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    orders = relationship("SalesOrder", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(OrderStatus), default=OrderStatus.draft)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    invoice = relationship("Invoice", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.unpaid)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("SalesOrder", back_populates="invoice")
