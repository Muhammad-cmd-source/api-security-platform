import os, time, hmac, hashlib, secrets
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import get_db
from .models import User

SECRET = os.getenv("SECRET_KEY", "dev-only-change-me-please-use-32-bytes!")  # nosec B105
ALGO = "HS256"
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${h}"


def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split("$")
    c = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return hmac.compare_digest(c, h)


def create_token(username: str) -> str:
    return jwt.encode({"sub": username, "exp": int(time.time()) + 3600}, SECRET, algorithm=ALGO)


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGO])["sub"]
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(401, "Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(401, "Invalid token")
    return user
