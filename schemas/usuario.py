from pydantic import BaseModel
from typing import Optional
class UsuarioCreate(BaseModel):
    nome : str
    email:str
    senha:str
    cidade : str
class UsuarioResponse(BaseModel):
    id:int
    nome:str
    email:str
    regiao : str

    class config:   
        from_attributes=True

class DadosResponse(BaseModel):
    id: int
    nome: str
    email: str
    cidade: Optional[str]
    regiao: Optional[str]
    class Config:
        orm_mode = True       
        