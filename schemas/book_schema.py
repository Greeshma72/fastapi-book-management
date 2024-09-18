from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.orm import Session

from db import models
from schemas.pydantic_models.book_model import BookCreate, ReviewCreate


def get_book(db, book_id: str):
    result = db.execute(select(models.Book).filter(models.Book.id == book_id))
    return result.scalars().first()


def get_books(db):
    result = db.execute(select(models.Book))
    books = result.scalars().all()
    return books


def create_book(db: Session, book: BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db, book_id: str, book: BookCreate):
    stmt = (
        sqlalchemy_update(models.Book)
        .where(models.Book.id == book_id)
        .values(**book.dict())
        .execution_options(synchronize_session="fetch")
    )
    db.execute(stmt)
    db.commit()
    return get_book(db, book_id)


def delete_book(db, book_id: str):
    stmt = (
        sqlalchemy_delete(models.Book)
        .where(models.Book.id == book_id)
        .execution_options(synchronize_session="fetch")
    )
    db.execute(stmt)
    return "book is deleted succesfully"


def get_review(db: AsyncSession, review_id: str):
    result = db.execute(select(models.Review).filter(models.Review.id == review_id))
    return result.scalars().first()


def get_reviews(db):
    result = db.execute(select(models.Review))
    return result.scalars().all()


def create_review(db, review: ReviewCreate, book_id: str):
    db_review = models.Review(**review.dict(), book_id=book_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db, review_id: str, review: ReviewCreate):
    stmt = (
        sqlalchemy_update(models.Review)
        .where(models.Review.id == review_id)
        .values(**review.dict())
        .execution_options(synchronize_session="fetch")
    )
    db.execute(stmt)
    return get_review(db, review_id)


def delete_review(db, review_id: str):
    stmt = (
        sqlalchemy_delete(models.Review)
        .where(models.Review.id == review_id)
        .execution_options(synchronize_session="fetch")
    )
    db.execute(stmt)
