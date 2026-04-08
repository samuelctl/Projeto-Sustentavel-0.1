from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import uuid4

from database.connection import get_db
from services.insights_service import gerar_insights_completos
from services.pdf_services import gerar_pdf_relatorio
from core.auth import get_usuario_logado

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.get("/relatorio")
def gerar_relatorio_pdf(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    insights = gerar_insights_completos(
        db=db,
        usuario_id=usuario.id,
        meses_projetados=3,
        janela_meses=3
    )

    caminho = f"relatorio_usuario_{usuario.id}_{uuid4().hex}.pdf"

    gerar_pdf_relatorio(insights, caminho)

    return FileResponse(
        path=caminho,
        filename="relatorio_financeiro.pdf",
        media_type="application/pdf"
    )