from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.simulacao import SimulacaoCreate
from models.consumo import Consumo
from models.usuario import Usuario
from models.simulacao import Simulacao
from models.tarifas import Tarifa
from database.connection import SessionLocal
from database.connection import get_db
from fastapi import HTTPException

router = APIRouter(tags=["Simulacoes"])

@router.post("/")
def criar_simulacao(dados:SimulacaoCreate,db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    tarifa = db.query(Tarifa).filter(
        Tarifa.regiao == usuario.regiao,
        Tarifa.tipo == dados.tipo
    ).first()
    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa não configurada para esta região!")
    
    valor_total = float(dados.consumo_valor) *  float(tarifa.valor)

    nova_simulacao = Simulacao(
        atividade=dados.atividade,
        tipo=dados.tipo,
        consumo_valor=dados.consumo_valor,
        valor_calculado=valor_total,
        usuario_id=usuario.id,
        id_tarifa=tarifa.id_tarifa,
        regiao_aplicada=usuario.regiao
    )   
    db.add(nova_simulacao)
    db.commit()
    db.refresh(nova_simulacao)
    return{
        "mensagem" : "Simulação Realizada!",
        "resultado":{
            "valor_unitario": tarifa.valor,
            "total":valor_total,
            "regiao" : usuario.regiao
        }
    }

@router.delete("/{simulacao_id}")
def deletar_simulacao(simulacao_id: int, db: Session = Depends(get_db)):
    db_simulacao = db.query(Simulacao).filter(Simulacao.id_simulacao == simulacao_id).first()
    if not db_simulacao:
        raise  HTTPException(status_code=404, detail="Simulação não encontrado")
    db.delete(db_simulacao)
    db.commit()
    return {"detail": "Deletado com sucesso"}

