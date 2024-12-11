from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List
from pydantic import BaseModel
from starlette import status

from database import SessionLocal
from sqlalchemy.orm import Session
from models import User

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta, datetime
import uuid


router = APIRouter(prefix="/auth", tags=["/auth"])

ALGORITHM = "HS256"
SECRET_KEY = "tnapoefq89-rh9-q38rh-9hg9-ry7yrw08r8wreru-q9u8re-n4y5-9qmx,/z[;d3ure3qjrj9qr]"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, user:CreateUserRequest):
    create_user_model = User(username = user.username, email = user.email, hashed_password = bcrypt_context.hash(user.password))
    db.add(create_user_model)
    db.commit()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED, response_model=Token)
def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User validation failed.")
    token = create_access_token(user.username, user.id, timedelta(minutes=60))
    return{"access_token":token, "token_type":"bearer"}


def authenticate_user(username:str, password:str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, id:str, expires_delta:timedelta):
    encode = {"sub":username, "id":str(id)}
    expires = datetime.utcnow()+expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2bearer)]):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        username:str = payload.get("sub")
        id: str = payload.get("id")

        if username is None or id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User validation failed.")
        
        return{"username":username, "id":id}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User validation failed.")