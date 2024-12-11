from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from database import SessionLocal, engine
import models, auth
from sqlalchemy.orm import Session

from pydantic import BaseModel

app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind = engine)

class PostBase(BaseModel):
    title: str
    body: str


# @app.post("new-post/")
# async def post(post:PostBase)