from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Variant as VariantModel, Product as ProductModel
from schemas import VariantCreate, Variant
from database import get_db

router = APIRouter(
    prefix="/variants",
    tags=["variants"]
)

# Create a new variant
@router.post("/", response_model=Variant)
def create_variant(variant: VariantCreate, db: Session = Depends(get_db)):
    # Check if the product exists
    product = db.query(ProductModel).filter(ProductModel.id == variant.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # # Check if the product allows variants
    # if not product.has_variants:
    #     raise HTTPException(status_code=400, detail="Product does not support variants")

    # Check if a variant with the same name already exists for the product
    existing_variant = db.query(VariantModel).filter(
        VariantModel.product_id == variant.product_id,
        VariantModel.name == variant.name
    ).first()

    if existing_variant:
        raise HTTPException(status_code=400, detail="Variant with the same name already exists for this product")

    # Create new variant if no duplicate is found
    new_variant = VariantModel(**variant.model_dump())
    db.add(new_variant)
    db.commit()
    db.refresh(new_variant)

    return new_variant



# Get all variants
@router.get("/", response_model=List[Variant])
def get_variants(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    variants = db.query(VariantModel).offset(skip).limit(limit).all()
    return variants

# Get variant by ID
@router.get("/{variant_id}", response_model=Variant)
def get_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = db.query(VariantModel).filter(VariantModel.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant

# Update variant by ID
@router.put("/{variant_id}", response_model=Variant)
def update_variant(variant_id: int, variant_update: VariantCreate, db: Session = Depends(get_db)):
    variant = db.query(VariantModel).filter(VariantModel.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    variant.name = variant_update.name
    variant.price = variant_update.price
    variant.stock = variant_update.stock
    db.commit()
    db.refresh(variant)
    return variant

# Delete variant by ID
@router.delete("/{variant_id}", response_model=Variant)
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = db.query(VariantModel).filter(VariantModel.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    db.delete(variant)
    db.commit()
    return variant
