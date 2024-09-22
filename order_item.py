# order_items.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from auth.jwt import get_current_customer  # Ensure this is your JWT verification function

router = APIRouter(prefix="/order_items", tags=["Order Items"])

@router.post("/", response_model=schemas.OrderItem, status_code=status.HTTP_201_CREATED)
def create_order_item(
    order_item_create: schemas.OrderItemCreate,
    db: Session = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)  # Add JWT dependency
):
    # Check if the order exists
    order = db.query(models.Order).filter(models.Order.id == order_item_create.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if the variant and product exist
    variant = db.query(models.Variant).filter(models.Variant.id == order_item_create.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    product = db.query(models.Product).filter(models.Product.id == order_item_create.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if variant.stock < order_item_create.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for variant")

    # Create the order item
    order_item = models.OrderItem(
        order_id=order_item_create.order_id,
        variant_id=order_item_create.variant_id,
        product_id=order_item_create.product_id,
        quantity=order_item_create.quantity,
        price_per_unit=variant.price
    )
    db.add(order_item)
    db.commit()
    db.refresh(order_item)

    # Update stock
    variant.stock -= order_item_create.quantity
    db.commit()

    return order_item

@router.get("/{order_item_id}", response_model=schemas.OrderItem)
def get_order_item(
    order_item_id: int,
    db: Session = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)  # Add JWT dependency
):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    return order_item

@router.put("/{order_item_id}", response_model=schemas.OrderItem)
def update_order_item(
    order_item_id: int,
    order_item_update: schemas.OrderItemCreate,
    db: Session = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)  # Add JWT dependency
):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    # Check if the variant and product exist
    variant = db.query(models.Variant).filter(models.Variant.id == order_item_update.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    product = db.query(models.Product).filter(models.Product.id == order_item_update.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if variant.stock < order_item_update.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for variant")

    # Update the order item
    order_item.variant_id = order_item_update.variant_id
    order_item.product_id = order_item_update.product_id
    order_item.quantity = order_item_update.quantity
    order_item.price_per_unit = variant.price

    db.commit()
    db.refresh(order_item)

    # Update stock
    # Restore previous stock
    prev_quantity = order_item.quantity
    variant.stock += prev_quantity

    # Reduce stock for new quantity
    variant.stock -= order_item_update.quantity
    db.commit()

    return order_item

@router.delete("/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(
    order_item_id: int,
    db: Session = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)  # Add JWT dependency
):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    # Restore stock before deleting
    variant = db.query(models.Variant).filter(models.Variant.id == order_item.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    variant.stock += order_item.quantity

    db.delete(order_item)
    db.commit()
    return None
