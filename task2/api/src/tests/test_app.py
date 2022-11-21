from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import create_database, drop_database
import pytest

from ..database import Base, DATABASE_URL
from ..main import app, get_db
from ..models import Product, Category, Association

engine = create_engine(DATABASE_URL + "test_db")

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def init():
    """
    Create the database and tables before the tests run.
    """
    create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    yield
    drop_database(engine.url)


@pytest.fixture(scope="class", autouse=True)
def test_session():
    """
    Create a new session for each test class.
    """
    db = TestingSessionLocal()

    yield db

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()
    print("test_session end")


def test_create_product():
    response = client.post("/products/", json={"name": "product1"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "product1",
        "categories": [],
    }


def test_create_category():
    response = client.post("/categories/", json={"name": "category1"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "category1",
        "products": [],
    }


def test_create_association(test_session: Session):
    product = Product(name="product1")
    category = Category(name="category1")
    test_session.add_all([product, category])
    test_session.commit()
    test_session.refresh(product)
    test_session.refresh(category)

    response = client.post(
        "/associations/", json={"product_id": product.id, "category_id": category.id}
    )
    assert response.status_code == 200
    assert response.json() == {
        "product": {
            "id": product.id,
            "name": "product1",
        },
        "category": {
            "id": category.id,
            "name": "category1",
        },
    }


def test_create_association_exists(test_session: Session):
    product = Product(name="product1")
    category = Category(name="category1")
    association = Association(product=product, category=category)
    test_session.add_all([product, category, association])
    test_session.commit()
    test_session.refresh(product)
    test_session.refresh(category)

    response = client.post(
        "/associations/", json={"product_id": product.id, "category_id": category.id}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Association already exists",
    }


def test_create_association_fail(test_session: Session):
    response = client.post("/associations/", json={"product_id": 1, "category_id": 1})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found",
    }


def test_create_association_fail2(test_session: Session):
    product = Product(name="product1")
    test_session.add(product)
    test_session.commit()
    test_session.refresh(product)

    response = client.post(
        "/associations/", json={"product_id": product.id, "category_id": 1}
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Category not found",
    }


@pytest.fixture(scope="class", autouse=False)
def get_methods_class_setup(request, test_session: Session):
    """
    Fixture to setup the TestGetMethods class
    """
    request.cls.products = [Product(name="product1"), Product(name="product2")]
    request.cls.categories = [Category(name="category1"), Category(name="category2")]
    request.cls.associations = [
        Association(
            product=request.cls.products[0], category=request.cls.categories[0]
        ),
        Association(
            product=request.cls.products[0], category=request.cls.categories[1]
        ),
        Association(
            product=request.cls.products[1], category=request.cls.categories[0]
        ),
    ]
    test_session.add_all(
        request.cls.products + request.cls.categories + request.cls.associations
    )
    test_session.commit()


class TestGetMethods:
    """
    Test all get methods
    """

    def test_get_product(self, get_methods_class_setup):
        response = client.get(f"/products/{self.products[0].id}/")
        assert response.status_code == 200
        assert response.json() == {
            "id": self.products[0].id,
            "name": "product1",
            "categories": [
                {"id": self.categories[0].id, "name": "category1"},
                {"id": self.categories[1].id, "name": "category2"},
            ],
        }

    def test_get_product_fail(self):
        response = client.get("/products/100/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Product not found"}

    def test_get_category(self):
        response = client.get(f"/categories/{self.categories[0].id}/")
        assert response.status_code == 200
        assert response.json() == {
            "id": self.categories[0].id,
            "name": "category1",
            "products": [
                {
                    "id": self.products[0].id,
                    "name": "product1",
                },
                {
                    "id": self.products[1].id,
                    "name": "product2",
                },
            ],
        }

    def test_get_category_fail(self):
        response = client.get("/categories/100/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Category not found"}

    def test_get_products(self):
        response = client.get("/products/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": self.products[0].id,
                "name": "product1",
                "categories": [
                    {
                        "id": self.categories[0].id,
                        "name": "category1",
                    },
                    {
                        "id": self.categories[1].id,
                        "name": "category2",
                    },
                ],
            },
            {
                "id": self.products[1].id,
                "name": "product2",
                "categories": [
                    {
                        "id": self.categories[0].id,
                        "name": "category1",
                    },
                ],
            },
        ]

    def test_get_categories(self):
        response = client.get("/categories/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": self.categories[0].id,
                "name": "category1",
                "products": [
                    {
                        "id": self.products[0].id,
                        "name": "product1",
                    },
                    {
                        "id": self.products[1].id,
                        "name": "product2",
                    },
                ],
            },
            {
                "id": self.categories[1].id,
                "name": "category2",
                "products": [
                    {
                        "id": self.products[0].id,
                        "name": "product1",
                    },
                ],
            },
        ]

    def test_get_associations(self):
        response = client.get("/associations/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "product": {
                    "id": self.products[0].id,
                    "name": "product1",
                },
                "category": {
                    "id": self.categories[0].id,
                    "name": "category1",
                },
            },
            {
                "product": {
                    "id": self.products[0].id,
                    "name": "product1",
                },
                "category": {
                    "id": self.categories[1].id,
                    "name": "category2",
                },
            },
            {
                "product": {
                    "id": self.products[1].id,
                    "name": "product2",
                },
                "category": {
                    "id": self.categories[0].id,
                    "name": "category1",
                },
            },
        ]
