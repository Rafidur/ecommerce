from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Customer as CustomerModel, Address as AddressModel
from schemas import CustomerCreate, Customer, AddressCreate
from database import get_db
from auth.jwt import get_current_customer  # Updated to reflect customer terminology
import bcrypt

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

# Create a new customer
@router.post("/", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Check if customer email already exists
    db_customer = db.query(CustomerModel).filter(CustomerModel.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(customer.password.encode('utf-8'), bcrypt.gensalt())

    # Create a new customer with hashed password
    new_customer = CustomerModel(email=customer.email, name=customer.name, password=hashed_password.decode('utf-8'))
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# Get all customers (requires authentication)
@router.get("/", response_model=List[Customer])
def get_customers(db: Session = Depends(get_db), current_customer: CustomerModel = Depends(get_current_customer)):
    customers = db.query(CustomerModel).all()  # You may want to apply pagination
    return customers

# Get customer by ID (requires authentication)
@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db), current_customer: CustomerModel = Depends(get_current_customer)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Update customer
@router.put("/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, updated_customer: CustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Hash the new password if it's being updated
    if updated_customer.password:
        customer.password = bcrypt.hashpw(updated_customer.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    customer.email = updated_customer.email
    customer.name = updated_customer.name
    db.commit()
    db.refresh(customer)
    return customer

# Delete customer (requires authentication)
@router.delete("/{customer_id}", response_model=Customer)
def delete_customer(customer_id: int, db: Session = Depends(get_db), current_customer: CustomerModel = Depends(get_current_customer)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return customer

# Create a new address for the customer (requires authentication)
@router.post("/{customer_id}/addresses", response_model=AddressCreate)
def create_address(customer_id: int, address: AddressCreate, db: Session = Depends(get_db), current_customer: CustomerModel = Depends(get_current_customer)):
    # Check if customer exists
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Handle default address logic (only one default address per customer)
    if address.is_default:
        db.query(AddressModel).filter(AddressModel.customer_id == customer_id).update(
            {"is_default": False},
            synchronize_session=False
        )
    
    # Create new address
    new_address = AddressModel(customer_id=customer_id, **address.dict())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address
