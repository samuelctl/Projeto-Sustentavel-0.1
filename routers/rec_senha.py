from fastapi import FastAPI, Depends, APIRouter, HTTPException
from core.email import enviar_email
from sqlalchemy.orm import Session
from database.connection import SessionLocal,get_db
from schemas.rec_senha import EsqueciSenhaRequest
from models.usuario import Usuario

router = APIRouter(tags=["Recuperar Senha"])

@router.post("/esqueci-senha")
def esqueci_senha(dados: EsqueciSenhaRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario:
        return {"mensagem": "Se o email existir, um link será enviado."}

    import secrets
    from datetime import datetime, timedelta

    token = secrets.token_urlsafe(32)

    usuario.reset_token = token
    usuario.reset_token_expira_em = datetime.utcnow() + timedelta(minutes=30)

    db.commit()

    link = f"http://localhost:3000/redefinir-senha?token={token}"
    mensagem = f"""
<div style="background-color:#F1F8F4; padding:40px 0; font-family:Arial, sans-serif;">
    
    <div style="max-width:520px; margin:auto; background:#FFFFFF; border-radius:14px; padding:35px; box-shadow:0 6px 20px rgba(0,0,0,0.05);">
        
        <!-- Header -->
        <div style="text-align:center; margin-bottom:20px;">
            <h2 style="color:#1B5E20; margin:0;">
                🌳 Ectotally
            </h2>
            <p style="color:#777; font-size:13px; margin-top:5px;">
                Controle inteligente de gastos
            </p>
        </div>

        <!-- Título -->
        <h3 style="color:#2E7D32; text-align:center; margin-bottom:20px;">
            Recuperação de senha
        </h3>

        <!-- Texto -->
        <p style="color:#444; font-size:15px;">
            Olá, <strong>{usuario.nome}</strong>
        </p>

        <p style="color:#555; font-size:15px; line-height:1.6;">
            Recebemos uma solicitação para redefinir sua senha.
            Para continuar, clique no botão abaixo:
        </p>

        <!-- Botão -->
        <div style="text-align:center; margin:30px 0;">
            <a href="{link}" 
               style="
                    background: linear-gradient(135deg, #2E7D32, #1B5E20);
                    color:white;
                    padding:14px 30px;
                    text-decoration:none;
                    border-radius:10px;
                    font-size:16px;
                    font-weight:bold;
                    display:inline-block;
                    box-shadow:0 4px 12px rgba(46,125,50,0.3);
               ">
                Redefinir senha
            </a>
        </div>

        <!-- Aviso -->
        <div style="background:#E8F5E9; padding:15px; border-radius:8px;">
            <p style="margin:0; font-size:14px; color:#2E7D32;">
                ⚠️ Este link expira em 30 minutos.
            </p>
        </div>

        <!-- Segurança -->
        <p style="color:#777; font-size:13px; margin-top:20px; text-align:center;">
            Se você não solicitou essa alteração, ignore este email com segurança.
        </p>

        <!-- Footer -->
        <hr style="border:none; border-top:1px solid #eee; margin:25px 0;">

        <p style="text-align:center; font-size:12px; color:#999;">
            © 2026 EcoControl • Todos os direitos reservados
        </p>

    </div>

</div>
"""

    enviar_email(
        destinatario=usuario.email,
        assunto="Recuperação de senha",
        mensagem_html=mensagem
    )

    return {"mensagem": "Email de recuperação enviado com sucesso!"}