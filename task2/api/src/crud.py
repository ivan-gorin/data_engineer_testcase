from sqlalchemy.orm import Session, joinedload

from . import models, schemas


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Product)
        .options(joinedload(models.Product.categories))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product(db: Session, product_id: int):
    return (
        db.query(models.Product)
        .options(joinedload(models.Product.categories))
        .filter(models.Product.id == product_id)
        .first()
    )


def create_product(db: Session, product: schemas.ProductBase):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Category)
        .options(joinedload(models.Category.products))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_category(db: Session, category_id: int):
    return (
        db.query(models.Category)
        .options(joinedload(models.Category.products))
        .filter(models.Category.id == category_id)
        .first()
    )


def create_category(db: Session, category: schemas.CategoryBase):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_associations(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Association)
        .options(
            joinedload(models.Association.product),
            joinedload(models.Association.category),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_association(db: Session, product_id: int, category_id: int):
    return (
        db.query(models.Association)
        .options(
            joinedload(models.Association.product),
            joinedload(models.Association.category),
        )
        .filter(
            models.Association.product_id == product_id,
            models.Association.category_id == category_id,
        )
        .first()
    )


def create_association(db: Session, association: schemas.AssociationBase):
    db_association = models.Association(**association.dict())
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    return db_association
