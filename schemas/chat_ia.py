from pydantic import BaseModel

class ChatIARequest(BaseModel):
    pergunta:str