from pydantic import BaseModel, ConfigDict
from typing import List,Optional


class ReviewBase(BaseModel):
    content: str
    rating: int


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: str
    book_id: str

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str
    author: str


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: str
    reviews: List[ReviewResponse] = []

    model_config = ConfigDict(from_attributes=True)
