from fastapi import APIRouter
from services.map_service import buscar_pontos

router = APIRouter(prefix="/mapa", tags=["Mapa"])

@router.get("/reciclagem")
def get_pontos(lat: float, lon: float):
    dados = buscar_pontos(lat, lon)
    return dados