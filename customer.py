from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Customer as CustomerModel, Address as AddressModel
from schemas import CustomerCreate, Customer, AddressCreate
from database import get_db

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
    
    # Create a new customer
    new_customer = CustomerModel(**customer.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# Get all customers
@router.get("/", response_model=List[Customer])
def get_customers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return customers

# Get customer by ID
@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
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
    
    customer.email = updated_customer.email
    customer.name = updated_customer.name
    db.commit()
    db.refresh(customer)
    return customer

# Delete customer
@router.delete("/{customer_id}", response_model=Customer)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return customer

# Create a new address for the customer

@router.post("/{customer_id}/addresses", response_model=AddressCreate)
def create_address(customer_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Handle default address logic (only one default address per customer)
    if address.is_default:
        # Set all other addresses for the customer to non-default
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
