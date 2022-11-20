from src.models import Category, Product, Association

from src.database import SessionLocal
from sqlalchemy.orm import joinedload

with SessionLocal() as db:
    product1 = Product(name="product1")
    product2 = Product(name="product2")
    category1 = Category(name="category1")
    category2 = Category(name="category2")

    association1 = Association(product=product1, category=category1)
    association2 = Association(product=product1, category=category2)
    association3 = Association(product=product2, category=category1)

    db.add_all([product1, product2, category1, category2, association1, association2, association3])
    db.commit()


    # print('Query 1')
    # q = db.query(Category).options(joinedload(Category.products)).where(Category.id == 1).first()
    # print('_'*100, 'COMMIT')
    # print(q.products)
    