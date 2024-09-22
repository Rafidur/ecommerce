from sqlalchemy import Float, create_engine, Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    addresses = relationship("Address", back_populates="customer",cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer",cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    address = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)

    customer = relationship("Customer", back_populates="addresses")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=True)
    order_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    total_price = Column(Integer, nullable=False)
    customer_email = Column(String, nullable=True)
    currency = Column(String, default='USD')

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="orders", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    variant_id = Column(Integer, ForeignKey('variants.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Integer, nullable=False)

    orders = relationship("Order", back_populates="order_items")
    variant = relationship("Variant", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=True)
    has_variants = Column(Boolean, default=False)
    stock = Column(Integer, nullable=True)
    description = Column(String)
    currency = Column(String, default='USD')

    variants = relationship("Variant", back_populates="product",cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")

class Variant(Base):
    __tablename__ = 'variants'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE' ), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)
    currency = Column(String, default='USD')

    product = relationship("Product", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="variant")



