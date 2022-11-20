from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/products/", response_model=List[schemas.Product], response_model_by_alias=False
)
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products


@app.get(
    "/products/{product_id}",
    response_model=schemas.Product,
    response_model_by_alias=False,
)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product not found")
    return db_product


@app.post("/products/", response_model=schemas.Product, response_model_by_alias=False)
def write_product(product: schemas.ProductBase, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)


@app.get(
    "/categories/", response_model=List[schemas.Category], response_model_by_alias=False
)
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@app.get(
    "/categories/{category_id}",
    response_model=schemas.Category,
    response_model_by_alias=False,
)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category not found")
    return category


@app.post(
    "/categories/", response_model=schemas.Category, response_model_by_alias=False
)
def write_category(category: schemas.CategoryBase, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)


@app.get(
    "/associations/",
    response_model=List[schemas.Association],
    response_model_by_alias=False,
    response_model_exclude={"product_id", "category_id"},
)
def read_associations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    associations = crud.get_associations(db, skip=skip, limit=limit)
    return associations


@app.post(
    "/associations/",
    response_model=schemas.Association,
    response_model_by_alias=False,
    response_model_exclude={"product_id", "category_id"},
)
def write_association(
    association: schemas.AssociationBase, db: Session = Depends(get_db)
):
    db_product = crud.get_product(db, product_id=association.product_id)
    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product not found",
        )
    db_category = crud.get_category(db, category_id=association.category_id)
    if db_category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Category not found",
        )
    db_association = crud.get_association(
        db, association.product_id, association.category_id
    )
    if db_association is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Association already exists",
        )
    return crud.create_association(db=db, association=association)
