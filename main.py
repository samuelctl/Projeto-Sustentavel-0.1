from fastapi import FastAPI
from database.connection import engine, Base
from models.usuario import Usuario
from schemas.usuario import UsuarioResponse
from routers.usuario import router as usuario_router
from routers.login import router as login_router
from routers.simulacao import router as simulacao_router
from routers.consumo import router as consumo_router
from routers.metas import router as metas_router
from routers.insights import router as futuro_router
from routers.rec_senha import router as rec_senha
from routers.ia import router as ia_router
from routers.pdf import router as pdf_router
from routers.mapa import router as mapa_router

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



Base.metadata.create_all(bind=engine)

app.include_router(usuario_router)
app.include_router(login_router,prefix="/login")
app.include_router(consumo_router, prefix="/consumos")
app.include_router(simulacao_router, prefix="/simulacao")
app.include_router(metas_router,prefix="/metas")
app.include_router(futuro_router)
app.include_router(rec_senha)
app.include_router(ia_router)
app.include_router(pdf_router)
app.include_router(mapa_router)