from pydantic import BaseModel, Field, ConfigDict 
from typing import Optional
# Aqui dentro do "schemas.py" os esquemas representam os dados que entram e saem da API


# Esquema para validação na criação de um usuário
class UserCreate(BaseModel):
    username: str
    password: str


# Esquema para exibir dados de um usuário (sem a senha)
class UserRead(BaseModel):
    id: int
    username: str

    # configura o classe para conseguir ler
    model_config = ConfigDict(from_attributes=True)  # from_attributes=True serve para o pydantic conseguir ler os objetos python


# Esquema da resposta do endpoint de login
class Token(BaseModel):
    access_token: str
    token_type: str
    

# Field serve para adicionar metadados, importante para documentação da api
class ContractData(BaseModel):
    contracting_party: Optional[str] = Field(description="O nome ou razão social da parte Contratante")
    contracted_party: Optional[str] = Field(description="O nome ou razão social da parte Contratada")
    contract_value: Optional[str] = Field(description="O valor monetário total do contrato")
    main_obligations: str = Field(description="Resumo das principais obrigações")
    additional_data: Optional[str] = Field(description="Outros dados importantes (objeto, vigência)")
    termination_clause: str = Field(description="Resumo da cláusula de rescisão")
    