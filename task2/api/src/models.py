from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from .database import Base


class Association(Base):
    __tablename__ = "association_table"

    product_id = Column(ForeignKey("products.id"), primary_key=True)
    category_id = Column(ForeignKey("categories.id"), primary_key=True)

    product = relationship("Product", back_populates="categories")
    category = relationship("Category", back_populates="products")

    product_name = association_proxy(target_collection="product", attr="name")
    category_name = association_proxy(target_collection="category", attr="name")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    categories = relationship("Association", back_populates="product")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    products = relationship("Association", back_populates="category")
