from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel
from starlette import status

from database import SessionLocal
from sqlalchemy.orm import Session

from models import User, Review, Post
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
    text: str
    post_id: int

