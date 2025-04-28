from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models_sql import User
from crud import get_user

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "szuperbiztos_kulcs"
ALGORITHM = "HS256"

class RegisterForm(BaseModel):
    email: str
    password: str

class LoginForm(BaseModel):
    email: str
    password: str

def create_token(email: str):
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@auth_router.post("/register")
def register(form: RegisterForm):
    db = SessionLocal()
    if get_user(db, form.email):
        raise HTTPException(status_code=400, detail="Felhasználó már létezik")
    hashed = pwd_context.hash(form.password)
    user = User(id=form.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    return {"message": "Sikeres regisztráció!"}

@auth_router.post("/login")
def login(form: LoginForm):
    db = SessionLocal()
    user = get_user(db, form.email)
    if not user or not pwd_context.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Hibás belépési adatok")
    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401)
        db = SessionLocal()
        user = get_user(db, email)
        if user is None:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401)