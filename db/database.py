from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from sqlalchemy import create_engine

from db.models import Base

# Use 'sqlite+aiosqlite' for SQLite with async support
DATABASE_URL = "sqlite:///./test1.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    with SessionLocal() as session:
        return session


def init_db():
    Base.metadata.create_all(engine)
