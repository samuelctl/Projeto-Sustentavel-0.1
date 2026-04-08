from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.simulacao import Simulacao
from models.tarifas import Tarifa
from schemas.simulacao import SimulacaoCreate
from core.auth import get_usuario_logado

router = APIRouter(prefix="/simulacoes", tags=["Simulacoes"])


@router.post("/")
def criar_simulacao(
    dados: SimulacaoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    tarifa = db.query(Tarifa).filter(
        Tarifa.regiao == usuario.regiao,
        Tarifa.tipo == dados.tipo
    ).first()

    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa não configurada para esta região!")

    valor_total = float(dados.consumo_valor) * float(tarifa.valor)

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

    return {
        "mensagem": "Simulação realizada!",
        "resultado": {
            "valor_unitario": tarifa.valor,
            "total": valor_total,
            "regiao": usuario.regiao
        }
    }


@router.delete("/{simulacao_id}")
def deletar_simulacao(
    simulacao_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    db_simulacao = db.query(Simulacao).filter(
        Simulacao.id_simulacao == simulacao_id,
        Simulacao.usuario_id == usuario.id
    ).first()

    if not db_simulacao:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")

    db.delete(db_simulacao)
    db.commit()

    return {"detail": "Deletado com sucesso"}