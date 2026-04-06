from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioResponse
from schemas.login import LoginRequest
from models.usuario import Usuario
from database.connection import SessionLocal
from core.security import verificar_senha
from database.connection import get_db
from fastapi import HTTPException

router = APIRouter(tags=["Login"])

@router.post("/",response_model=UsuarioResponse)
def login(dados:LoginRequest,db:Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha): 
        raise HTTPException(status_code=400, detail="Email ou senha inválidos!") 
    return usuario
