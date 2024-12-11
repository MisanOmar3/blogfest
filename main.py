from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, Optional
from database import SessionLocal, engine
import models, auth
from sqlalchemy.orm import Session

from pydantic import BaseModel
from starlette import status

app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]

class PostBase(BaseModel):
    title: str
    body: str

class UpdatePostBase(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None


@app.post("/new-post", status_code=status.HTTP_201_CREATED)
async def post(user:user_dependency, db:db_dependency, post:PostBase):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Authentication failed.")
    post_create_model = models.Post(title = post.title, body = post.body, owner = user["id"])
    db.add(post_create_model)
    db.commit()


@app.get("/posts", status_code=status.HTTP_200_OK)
async def get_posts(user:user_dependency, db:db_dependency, title:Optional[str] = None):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    response = db.query(models.Post).all()
    if title:
        posts = []
        for post in response:
            if title in post.title:
                posts.append(post)
        response = posts

    return {"posts":response}



@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
def get_post_detail(user: user_dependency, db:db_dependency, id:int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    response = db.query(models.Post).filter(models.Post.id == id).first()
    return response



@app.patch("/posts/{id}/update", status_code=status.HTTP_202_ACCEPTED)
def patch(id:int, update_post:UpdatePostBase, user:user_dependency, db:db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")    
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if str(post.owner) != str(user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this.")
    if update_post.body:
        post.body = update_post.body
    if update_post.title:
        post.title = update_post.title
    db.commit()
    return{f"message":"post {id} has been updated successfully!"}



@app.delete("/posts/{id}/delete")
def delete_post(id:int, user:user_dependency, db:db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if str(post.owner) != str(user["id"]):
        print(user["id"])
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this.")
    db.delete(post)
    db.commit()
    return{"message":"Post deleted successfully."}