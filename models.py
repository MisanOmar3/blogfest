from sqlalchemy import Column, Integer, UUID, String, ForeignKey, Text, Enum as SQLENUM
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base
from enum import Enum

class User(Base):
    __tablename__ = "users"
    
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner = Column(ForeignKey("users.id", ondelete="CASCADE"))
    body = Column(Text)

class Rating(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    owner = Column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id = Column(ForeignKey("posts.id", ondelete="CASCADE"))
    rating = Column("rating", SQLENUM(Rating), nullable=True)