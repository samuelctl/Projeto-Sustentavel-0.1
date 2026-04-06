from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from database.connection import SessionLocal 
from database.connection import SessionLocal
from fastapi.security import OAuth2PasswordBearer
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")

get_db()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha : str):
    return pwd_context.hash(senha)

def verificar_senha(senha:str, hash:str):
    return pwd_context.verify(senha, hash)