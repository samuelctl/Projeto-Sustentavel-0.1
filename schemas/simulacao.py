from pydantic import BaseModel
from decimal import Decimal
class SimulacaoCreate(BaseModel):
    atividade : str
    consumo_valor :Decimal
    tipo: str
    usuario_id : int