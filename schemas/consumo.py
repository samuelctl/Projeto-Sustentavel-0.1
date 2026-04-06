from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class ConsumoCreate(BaseModel):
    tipo : str
    gasto : Decimal
    usuario_id : int
    data : datetime 
    class Config:
        from_attributes = True  