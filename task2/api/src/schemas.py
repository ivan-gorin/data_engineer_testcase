from pydantic import BaseModel, Field
from typing import List


class ProductBase(BaseModel):
    name: str = Field(alias="product_name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ProductRead(ProductBase):
    id: int = Field(alias="product_id")


class CategoryBase(BaseModel):
    name: str = Field(alias="category_name")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class CategoryRead(CategoryBase):
    id: int = Field(alias="category_id")


class AssociationBase(BaseModel):
    product_id: int
    category_id: int

    class Config:
        orm_mode = True


class Product(ProductRead):
    categories: List[CategoryRead]


class Category(CategoryRead):
    products: List[ProductRead]


class Association(AssociationBase):
    product: ProductRead
    category: CategoryRead
