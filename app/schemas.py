from pydantic import BaseModel, Field
from typing import Optional


# Esquema para validação na criação de um usuário
class UserCreate(BaseModel):
    username: str
    password: str

# Esquema para exibir dados de um usuário (sem a senha!)
class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True # Ajuda o Pydantic a ler dados de modelos do banco

# Esquema da resposta do endpoint de login
class Token(BaseModel):
    access_token: str
    token_type: str
    

class ContractData(BaseModel):
    contracting_party: Optional[str] = Field(description="O nome ou razão social da parte Contratante")
    contracted_party: Optional[str] = Field(description="O nome ou razão social da parte Contratada")
    contract_value: Optional[str] = Field(description="O valor monetário total do contrato")
    main_obligations: str = Field(description="Resumo das principais obrigações")
    additional_data: Optional[str] = Field(description="Outros dados importantes (objeto, vigência)")
    termination_clause: str = Field(description="Resumo da cláusula de rescisão")