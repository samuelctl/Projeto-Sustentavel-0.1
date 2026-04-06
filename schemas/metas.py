from pydantic import BaseModel
from datetime import date
from decimal import Decimal

# Schema base com os campos comuns
class MetasBase(BaseModel):
    tipo_meta: str
    valor_objetivo: Decimal
    data_inicio: date
    data_fim: date
# Schema usado para criar uma meta
class MetasCreate(MetasBase):
    usuario_id: int
# Schema usado para retornar dados da API
class MetasResponse(MetasBase):
    id_meta: int
    usuario_id: int

    class Config:
        from_attributes = True  # necessário para SQLAlchemy 