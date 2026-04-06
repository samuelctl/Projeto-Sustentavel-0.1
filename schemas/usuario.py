from pydantic import BaseModel

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
        