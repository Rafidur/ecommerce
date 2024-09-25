from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from auth.jwt import get_current_customer  
import models, schemas
from database import get_db
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/api", tags=["orders"])

# Route to create a new order
@router.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order_create: schemas.OrderCreate, db: Session = Depends(get_db), current_customer: models.Customer = Depends(get_current_customer)):
    total_price = 0
    product_ids = set()

    # First, check if all items in the order have sufficient stock and calculate total price
    for item in order_create.order_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # If the product has variants
        if product.has_variants:
            if item.variant_id is None:
                raise HTTPException(status_code=400, detail=f"Variant ID is required for product '{product.name}'")
            
            variant = db.query(models.Variant).filter(models.Variant.id == item.variant_id).first()
            if not variant:
                raise HTTPException(status_code=404, detail=f"Variant not found for product '{product.name}'")
            
            # Check stock for variant
            if variant.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for variant '{variant.name}'")
            
            # Calculate total price for variant
            total_price += item.quantity * variant.price
            variant.stock -= item.quantity  # Update stock for the variant
            db.add(variant)  # Add the stock change to the session
        else:
            # For products without variants, check stock and price directly on the product
            if item.variant_id is not None:
                raise HTTPException(status_code=400, detail=f"Product '{product.name}' does not have variants, variant_id should be null")
            
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product '{product.name}'")
            
            # Calculate total price for product without variants
            total_price += item.quantity * product.price
            product.stock -= item.quantity  # Update stock for the product
            db.add(product)  # Add the stock change to the session

        product_ids.add(item.product_id)

    # Create the order
    order = models.Order(
        customer_id=current_customer.id,
        customer_email=current_customer.email,  # Capture email for the order
        order_date=datetime.now(),
        status="pending",
        total_price=total_price  # Set total price now that it's calculated
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items
    for item in order_create.order_items:
        # For products with variants, use variant_id
        if product.has_variants and item.variant_id is not None:
            order_item = models.OrderItem(
                order_id=order.id,
                variant_id=item.variant_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=variant.price
            )
        else:
            order_item = models.OrderItem(
                order_id=order.id,
                variant_id=None,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=product.price
            )

        db.add(order_item)
        db.commit()
        db.refresh(order_item)

    return order

@router.post("/orders/guest/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_guest_order(order_create: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Use None for customer_id since there's no authenticated customer
    return _process_order(order_create, db, customer_id=None)

def _process_order(order_create: schemas.OrderCreate, db: Session, customer_id: Optional[int]):
    total_price = 0
    product_ids = set()

    # First, check if all items in the order have sufficient stock and calculate total price
    for item in order_create.order_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # If the product has variants
        if product.has_variants:
            if item.variant_id is None:
                raise HTTPException(status_code=400, detail=f"Variant ID is required for product '{product.name}'")
            
            variant = db.query(models.Variant).filter(models.Variant.id == item.variant_id).first()
            if not variant:
                raise HTTPException(status_code=404, detail=f"Variant not found for product '{product.name}'")
            
            # Check stock for variant
            if variant.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for variant '{variant.name}'")
            
            # Calculate total price for variant
            total_price += item.quantity * variant.price
            variant.stock -= item.quantity  # Update stock for the variant
            db.add(variant)  # Add the stock change to the session
        else:
            # For products without variants, check stock and price directly on the product
            if item.variant_id is not None:
                raise HTTPException(status_code=400, detail=f"Product '{product.name}' does not have variants, variant_id should be null")
            
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product '{product.name}'")
            
            # Calculate total price for product without variants
            total_price += item.quantity * product.price
            product.stock -= item.quantity  # Update stock for the product
            db.add(product)  # Add the stock change to the session

        product_ids.add(item.product_id)

    # Create the order
    order = models.Order(
        customer_id=customer_id,
        customer_email=order_create.customer_email if customer_id is None else None,  # Capture email for guest orders
        order_date=datetime.now(),
        status="pending",
        total_price=total_price  # Set total price now that it's calculated
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items
    for item in order_create.order_items:
        if product.has_variants and item.variant_id is not None:
            order_item = models.OrderItem(
                order_id=order.id,
                variant_id=item.variant_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=variant.price
            )
        else:
            order_item = models.OrderItem(
                order_id=order.id,
                variant_id=None,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=product.price
            )

        db.add(order_item)
        db.commit()
        db.refresh(order_item)

    return order


# Get all orders (requires authentication)
@router.get("/", response_model=List[schemas.Order])
def get_all_orders(db: Session = Depends(get_db), current_customer: models.Customer = Depends(get_current_customer)):
    orders = db.query(models.Order).filter(models.Order.customer_id == current_customer.id).options(joinedload(models.Order.order_items)).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

# Route to get an order by ID (requires authentication)
@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db), current_customer: models.Customer = Depends(get_current_customer)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.customer_id == current_customer.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Route to update an order's status (requires authentication)
@router.put("/{order_id}", response_model=schemas.Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db), current_customer: models.Customer = Depends(get_current_customer)):
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "canceled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.customer_id == current_customer.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)
    return order

# Route to get all orders for a customer (requires authentication)
@router.get("/customers/{customer_id}/orders", response_model=List[schemas.Order])
def get_customer_orders(customer_id: int, db: Session = Depends(get_db), current_customer: models.Customer = Depends(get_current_customer)):
    if current_customer.id != customer_id:
        raise HTTPException(status_code=403, detail="Not authorized to access these orders")

    orders = db.query(models.Order).filter(models.Order.customer_id == customer_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer")
    return orders

# Route to delete an order by ID (requires authentication)
@router.delete("/{order_id}", response_model=schemas.Order)
def delete_order(order_id: int, db: Session = Depends(get_db), current_customer: models.Customer = Depends(get_current_customer)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.customer_id == current_customer.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if there are any items associated with the order
    order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    if order_items:
        for item in order_items:
            db.delete(item)

    db.delete(order)
    db.commit()
    return order
