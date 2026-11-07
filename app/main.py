from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import User, Task
from .auth import hash_password, verify_password, create_token, current_user

Base.metadata.create_all(engine)
app = FastAPI(title="API & Security Automation Platform")
STATIC = Path(__file__).resolve().parent.parent / "static"


@app.middleware("http")
async def security_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


class Creds(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", status_code=201)
def register(c: Creds, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == c.username).first():
        raise HTTPException(409, "Username taken")
    db.add(User(username=c.username, password_hash=hash_password(c.password)))
    db.commit()
    return {"username": c.username}


@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Bad credentials")
    return {"access_token": create_token(user.username), "token_type": "bearer"}


@app.get("/tasks")
def list_tasks(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Task).filter(Task.owner_id == user.id).all()
    return [{"id": t.id, "title": t.title} for t in rows]


@app.post("/tasks", status_code=201)
def create_task(t: TaskIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    task = Task(title=t.title, owner_id=user.id)
    db.add(task)
    db.commit()
    return {"id": task.id, "title": task.title}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(404, "Not found")
    db.delete(task)
    db.commit()
