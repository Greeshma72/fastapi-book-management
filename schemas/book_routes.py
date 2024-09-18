from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import User, Book, Review
from schemas import book_schema
from schemas.pydantic_models.book_model import BookCreate, ReviewCreate, ReviewResponse, BookResponse
from schemas.pydantic_models.user_schema import UserCreate
from db.database import get_session, get_db
from security.auth import get_current_user
from utilities.utils import create_access_token

router = APIRouter()


@router.post("/books/", response_model=BookCreate)
def create_book(book: BookCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return book_schema.create_book(db=db, book=book)


@router.get("/books/books/", response_model=List[BookResponse])
def read_books(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    books = db.query(Book).all()
    book_responses = []
    for book in books:
        reviews = db.query(Review).filter_by(book_id=book.id).all()
        review_responses = [
            ReviewResponse(id=review.id, content=review.content, rating=review.rating, book_id=review.book_id)
            for review in reviews
        ]
        book_responses.append(BookResponse(id=book.id, title=book.title, author=book.author, reviews=review_responses))
    return book_responses


@router.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: str, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter_by(id=book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: str, book: BookCreate, db: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter_by(id=book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book_schema.update_book(db=db, book_id=db_book.id, book=book)


@router.delete("/books/{book_id}")
def delete_book(book_id: str, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter_by(id=book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book_schema.delete_book(db=db, book_id=db_book.id)


@router.post("/books/{book_id}/reviews/", response_model=ReviewResponse)
def create_review_for_book(book_id: str, review: ReviewCreate, db: Session = Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter_by(id=current_user.id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book_schema.create_review(db=db, review=review, book_id=book_id)


@router.get("/reviews/", response_model=List[ReviewResponse])
def read_reviews(db: Session = Depends(get_session),
                 current_user: User = Depends(get_current_user)):
    reviews = db.query(Review).join(Book).all()
    return reviews


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
def read_review(review_id: str, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_review = db.query(Review).join(Book).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(review_id: str, review: ReviewCreate, db: Session = Depends(get_session),
                  current_user: User = Depends(get_current_user)):
    db_review = db.query(Review).join(Book).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return book_schema.update_review(db=db, review_id=review_id, review=review)


@router.delete("/reviews/{review_id}")
def delete_review(review_id: str, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_review = db.query(Review).join(Book).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return book_schema.delete_review(db=db, review_id=review_id)
