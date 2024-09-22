from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/addresses", tags=["Addresses"])

@router.post("/", response_model=schemas.Address, status_code=status.HTTP_201_CREATED)
def create_address(address_create: schemas.AddressCreateMain, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == address_create.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if address_create.is_default:
        # Set all other addresses for the customer to non-default
        db.query(models.Address).filter(models.Address.customer_id == customer.id).update(
            {models.Address.is_default: False},
            synchronize_session=False
        )
    
    # Create new address
    new_address = models.Address(
        customer_id=address_create.customer_id,
        address=address_create.address,  
        is_default=address_create.is_default
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

@router.get("/{address_id}", response_model=schemas.Address)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.put("/{address_id}", response_model=schemas.Address)
def update_address(address_id: int, address_update: schemas.AddressCreateMain, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Check if the new address is being set as default
    if address_update.is_default:
        # Set all other addresses for the customer to non-default
        db.query(models.Address).filter(models.Address.customer_id == address.customer_id).update(
            {models.Address.is_default: False},
            synchronize_session=False
        )
    
    # Update the address fields
    address.address = address_update.address
    address.is_default = address_update.is_default

    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()
    return None
