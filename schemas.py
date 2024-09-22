from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional


# Address Model
class AddressBase(BaseModel):
    address: str
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressCreateMain(AddressBase):
    customer_id: int
    
class Address(AddressBase):
    id: int
    customer_id: int

    class Config:
        orm_mode = True

# Customer Model
class CustomerBase(BaseModel):
    email: EmailStr
    name: str

class CustomerCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
   

class Customer(CustomerBase):
    id: int
    addresses: List[Address] = []

    class Config:
        orm_mode = True

# Login Schema
class Login(BaseModel):
    email: EmailStr
    password: str


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Variant Model
class VariantBase(BaseModel):
    name: str
    price: float
    stock: int
    currency: Optional[str]
    

class VariantCreate(VariantBase):
    product_id: int

class Variant(VariantBase):
    id: int
    product_id: int

    class Config:
        orm_mode = True
        


# Product Model
class ProductBase(BaseModel):
    name: str
    description: str
    has_variants: Optional[bool] = False
    
    
    
class ProductCreateSolo(ProductBase):
    stock: Optional[int]
    price: Optional[float]
    currency: Optional[str]
    
    
class ProductCreate(ProductBase):
    has_variants: Optional[bool] = True

class Product(ProductBase):
    id: int
    variants: List[Variant] = []

    class Config:
        orm_mode = True

# OrderItem Model
class OrderItemBase(BaseModel):
    quantity: int
    #price: float  # This is calculated as quantity * variant.price

class OrderItemCreate(OrderItemBase):
    product_id: int
    variant_id: Optional[int] 

class OrderItem(BaseModel):
    id: int
    order_id: int
    product_id: int
    variant_id: Optional[int] 
    quantity: int

    class Config:
        orm_mode = True
        
    

# Order Model
class OrderBase(BaseModel):
    order_date: datetime
    status: str
    total_price: float  # This is auto-calculated based on order items
    
   
class OrderCreate(BaseModel):
    customer_email: EmailStr
    customer_name: Optional[str] = None
    order_items: List[OrderItemCreate] 
    create_account: bool = True
    currency: Optional[str]

class Order(OrderBase):
    id: int
    customer_id: Optional[int]
    order_items: List[OrderItem]
    customer_email: Optional[str]

    class Config:
        orm_mode = True