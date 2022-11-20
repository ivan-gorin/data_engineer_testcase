import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/api_db"
# engine = create_engine(os.environ.get("DATABASE_URL"))
engine = create_engine(DATABASE_URL, echo=True, query_cache_size=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
