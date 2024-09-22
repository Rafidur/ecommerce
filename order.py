
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import EmailStr
import models, schemas
from database import get_db
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/api", tags=["orders"])

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/api", tags=["orders"])

# Route to create a new order

# Route to create a new order
@router.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order_create: schemas.OrderCreate, db: Session = Depends(get_db)):
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

    # If stock is sufficient for all items, proceed with creating the customer and order
    customer_id = None

    if order_create.create_account:
        # Fetch the customer by email
        customer = db.query(models.Customer).filter(models.Customer.email == order_create.customer_email).first()

        if not customer:
            # Create a new customer if none is found and create_account is True
            new_customer = models.Customer(
                email=order_create.customer_email,
                name=order_create.customer_name or "Unknown"  # Use provided name or default to "Unknown"
            )
            db.add(new_customer)
            db.flush()  # Flush to get the ID of the newly added customer
            customer_id = new_customer.id  # Get the new customer ID
            db.commit()
            db.refresh(new_customer)
        else:
            customer_id = customer.id
    else:
        # If no account is to be created, no customer ID is linked
        customer_id = None

    # Create the order
    order = models.Order(
        customer_id=customer_id,
        customer_email=order_create.customer_email if not order_create.create_account else None,  # Capture email for guest
        order_date=datetime.now(),  # Adjust as needed
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
                variant_id=variant.variant_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=variant.price
            )
        else:
            order_item = models.OrderItem(
                order_id=order.id,
                variant_id=None,  # No variant for products without variants
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=product.price
            )

        db.add(order_item)
        db.commit()
        db.refresh(order_item)

    return order



#get all orders
@router.get("/", response_model=List[schemas.Order])
def get_all_orders(db: Session = Depends(get_db)):
    # Use joinedload to eagerly load related order_items
    orders = db.query(models.Order).options(joinedload(models.Order.order_items)).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders



# Route to get an order by ID
@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Route to update an order's status
@router.put("/{order_id}", response_model=schemas.Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "canceled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)
    return order

# Route to get all orders for a customer
@router.get("/customers/{customer_id}/orders", response_model=List[schemas.Order])
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.customer_id == customer_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer")
    return orders

# Route to get all orders for a customer (by customer_id or email)
@router.get("/customers-and-guests/{customer_id}/orders", response_model=List[schemas.Order])
def get_customer_orders(customer_id: int, email: Optional[str] = None, db: Session = Depends(get_db)):
    # Query for orders where customer_id matches
    query = db.query(models.Order).filter(models.Order.customer_id == customer_id)

    # If email is provided, add additional filter for guest orders with the same email
    if email:
        query = query.union(db.query(models.Order).filter(models.Order.customer_email == email))

    orders = query.all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer or email")

    return orders



# Route to delete an order by ID
@router.delete("/{order_id}", response_model=schemas.Order)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if there are any items associated with the order
    order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    if order_items:
        # Optionally handle or remove order items if needed
        for item in order_items:
            db.delete(item)

    db.delete(order)
    db.commit()
    return order
