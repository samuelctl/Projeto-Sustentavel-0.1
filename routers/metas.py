from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.metas import Meta
from models.usuario import Usuario
from schemas.metas import MetasCreate, MetasResponse
from database.connection import get_db
router = APIRouter(tags=["Metas"])


@router.post("/", response_model=MetasResponse)
def criar_meta(dados: MetasCreate, db: Session = Depends(get_db)):
    # Primeiro verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Cria a nova meta com os dados recebidos
    nova_meta = Meta(
        tipo_meta=dados.tipo_meta,
        valor_objetivo=dados.valor_objetivo,
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim,
        usuario_id=dados.usuario_id
    )

    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)

    return nova_meta

@router.get("/usuario/{usuario_id}", response_model=list[MetasResponse])
def listar_metas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    # Retorna apenas as metas do usuário informado
    metas = db.query(Meta).filter(Meta.usuario_id == usuario_id).all()
    return metas

@router.put("/{meta_id}", response_model=MetasResponse)
def editar_meta(meta_id: int, dados: MetasCreate, db: Session = Depends(get_db)):
    # Procura a meta que será editada
    meta = db.query(Meta).filter(Meta.id_meta == meta_id).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    # Verifica se o usuário informado existe
    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Atualiza os campos da meta
    meta.tipo_meta = dados.tipo_meta
    meta.valor_objetivo = dados.valor_objetivo
    meta.data_inicio = dados.data_inicio
    meta.data_fim = dados.data_fim
    meta.usuario_id = dados.usuario_id

    db.commit()
    db.refresh(meta)

    return meta


@router.delete("/{meta_id}")
def deletar_meta(meta_id: int, db: Session = Depends(get_db)):
    # Procura a meta pelo id antes de deletar
    meta = db.query(Meta).filter(Meta.id_meta == meta_id).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    db.delete(meta)
    db.commit()

    return {"detail": "Meta deletada com sucesso"}