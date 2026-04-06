from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioResponse, UsuarioCreate
from schemas.consumo import ConsumoCreate
from models.usuario import Usuario
from models.consumo import Consumo
from database.connection import SessionLocal
from fastapi import HTTPException
from database.connection import get_db

router = APIRouter(tags=["Consumos"])


@router.post("/")
def criar_consumo(dados: ConsumoCreate, db: Session = Depends(get_db)):
    novo_cons = Consumo(
        tipo=dados.tipo,
        gasto=dados.gasto,
        usuario_id=dados.usuario_id,
        data=dados.data
    )
    db.add(novo_cons)
    db.commit()
    db.refresh(novo_cons)
    return {"status": "Consumo registrado!"}

@router.get("/usuario/{u_id}")
def listar_consumos(u_id: int, db: Session = Depends(get_db)):
    # Busca todos os consumos onde o usuario_id é igual ao ID passado na URL
    lista = db.query(Consumo).filter(
        Consumo.usuario_id == u_id
    ).all()
    return lista

@router.put("/{consumo_id}")
def editar_consumo(consumo_id: int, dados: ConsumoCreate, db: Session = Depends(get_db)):
    # Busca o consumo pelo id
    db_consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()

    # Se não encontrar, retorna erro 404
    if not db_consumo:
        raise HTTPException(status_code=404, detail="Consumo não encontrado")

    # Atualiza os campos com os novos dados enviados
    db_consumo.tipo = dados.tipo
    db_consumo.gasto = dados.gasto
    db_consumo.usuario_id = dados.usuario_id
    db_consumo.data = dados.data

    # Salva as alterações no banco
    db.commit()
    db.refresh(db_consumo)

    # Retorna o consumo atualizado
    return db_consumo

@router.delete("/{consumo_id}")
def deletar_consumo(consumo_id: int, db: Session = Depends(get_db)):
    db_consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()
    if not db_consumo:
        raise HTTPException(status_code=404, detail="Consumo não encontrado")
    db.delete(db_consumo)
    db.commit()
    return {"detail": "Deletado com sucesso"}