from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from starlette import status

from database import SessionLocal
from sqlalchemy.orm import Session

from models import User, Review, Post, Rating
from auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["/reviews"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class PostReviewBase(BaseModel):
    text: Optional[str] = None
    post_id: int
    rating: Rating = Field(default = Rating)

class UpdateReviewBase(BaseModel):
    text: Optional[str] = None
    rating: Rating = Field(default = None)


@router.post("/new-review", status_code= status.HTTP_201_CREATED)
def post_review(review:PostReviewBase, db:db_dependency, user:user_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Authentication failed.")
    create_post_model = Review(text = review.text, owner = user['id'], post_id = review.post_id, rating = review.rating)
    db.add(create_post_model)
    db.commit()
    return {"message":"Review posted successfully."}

@router.get("/{id}/get")
def retrieve_review(user: user_dependency, db:db_dependency, id:int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Authentication failed.")
    review = db.query(Review).filter(Review.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    return review

@router.get("/get")
def get_reviews(user:user_dependency, db:db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    reviews = db.query(Review).all()
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    return reviews

@router.delete("/{id}/delete")
def delete_review(user:user_dependency, db:db_dependency, id:int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    review = db.query(Review).filter(Review.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    if str(review.owner) is not str(user["id"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this.")
    db.delete(review)
    db.commit()
    return {"message":"Review deleted successfully."}

@router.patch("/{id}/update")
def update_review(review_update: UpdateReviewBase, user:user_dependency, db:db_dependency, id:int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    review = db.query(Review).filter(Review.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    if str(review.owner) is not str(user["id"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have access to this.")
    review.text = review_update.text
    review.rating = review_update.rating
    db.commit()
    return {"message":"Review updated successfully."}