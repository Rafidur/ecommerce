from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Product as ProductModel, Variant as VariantModel
from schemas import ProductCreate, Product, ProductCreateSolo, VariantCreate, Variant
from database import get_db
from fastapi import HTTPException

router = APIRouter(
    prefix="/products",
    tags=["products"]
)



@router.post("/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check if a product with the same name already exists
    existing_product = db.query(ProductModel).filter(ProductModel.name == product.name).first()
    
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    

    # Create a new product
    new_product = ProductModel(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.post("/solo", response_model=ProductCreateSolo)
def create_product_solo(product: ProductCreateSolo, db: Session = Depends(get_db)):
    # Check if a product with the same name already exists
    existing_product = db.query(ProductModel).filter(ProductModel.name == product.name).first()
    
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    

    # Create a new product
    new_product = ProductModel(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# Get all products
@router.get("/", response_model=List[Product])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(ProductModel).offset(skip).limit(limit).all()
    return products

# Get product by ID
@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update a product by ID
@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = updated_product.name
    product.desc = updated_product.desc
    db.commit()
    db.refresh(product)
    return product

# Delete a product by ID
@router.delete("/{product_id}", response_model=Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return product

# Create a new variant for a product
@router.post("/{product_id}/variants", response_model=Variant)
def create_variant(variant: VariantCreate, db: Session = Depends(get_db)):
    # Check if the product exists
    product = db.query(ProductModel).filter(ProductModel.id == variant.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if the product allows variants
    if not product.has_variants:
        raise HTTPException(status_code=400, detail="Product does not support variants")

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



# Get all variants for a product
@router.get("/{product_id}/variants", response_model=List[Variant])
def get_variants(product_id: int, db: Session = Depends(get_db)):
    variants = db.query(VariantModel).filter(VariantModel.product_id == product_id).all()
    return variants

# Get variant by ID
@router.get("/{product_id}/variants/{variant_id}", response_model=Variant)
def get_variant(product_id: int, variant_id: int, db: Session = Depends(get_db)):
    variant = db.query(VariantModel).filter(VariantModel.product_id == product_id, VariantModel.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant
