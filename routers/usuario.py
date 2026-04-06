from fastapi import FastAPI, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioResponse, UsuarioCreate
from models.usuario import Usuario
from database.connection import SessionLocal
from core.security import gerar_hash
from routers import regiao
from database.connection import get_db
router = APIRouter(tags=["Usuarios"])


@router.post("/usuario", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Gera o hash da senha antes de salvar no banco
    senha_hash = gerar_hash(usuario.senha)

    # Busca a região com base na cidade informada
    localidade = regiao.get_regiao_por_cidade(usuario.cidade)
    nome_regiao = "Não informada"

    # Se encontrar a cidade, pega o nome da região
    if localidade and isinstance(localidade, dict):
        nome_regiao = localidade.get("regiao", "Não encontrada")

    # Cria o objeto do usuário
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=senha_hash,
        cidade=usuario.cidade,
        regiao=nome_regiao
    )

    # Salva no banco
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.put("/usuario/{usuario_id}", response_model=UsuarioResponse)
def editar_usuario(usuario_id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Procura o usuário pelo id
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    # Se não encontrar, retorna erro 404
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Atualiza a região com base na nova cidade informada
    localidade = regiao.get_regiao_por_cidade(usuario.cidade)
    nome_regiao = "Não informada"

    if localidade and isinstance(localidade, dict):
        nome_regiao = localidade.get("regiao", "Não encontrada")

    # Atualiza os campos do usuário
    db_usuario.nome = usuario.nome
    db_usuario.email = usuario.email
    db_usuario.senha = gerar_hash(usuario.senha)
    db_usuario.cidade = usuario.cidade
    db_usuario.regiao = nome_regiao

    # Salva as alterações
    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@router.delete("/usuario/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    # Procura o usuário no banco
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    # Se não existir, retorna erro
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Remove o usuário do banco
    db.delete(db_usuario)
    db.commit()

    return {"detail": "Usuário deletado com sucesso"}