from sqlalchemy import Column, Boolean, Integer, UUID, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base
from pydantic import EmailStr

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

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    owner = Column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id = Column(ForeignKey("posts.id", ondelete="CASCADE"))