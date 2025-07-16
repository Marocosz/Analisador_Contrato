from typing import Optional
from sqlmodel import Field, SQLModel
# Diferente do "schemas.py" aqui temos a representação dos dados para o banco de dados

class User(SQLModel, table=True):
    # O ID é Optional, visto que a API dará para o usuário automaticamente seu "ID", de forma incremental, então precisamos disso
    # para o pydantic/sqlmodel não dar erro visto que seria "None" inicialmente e não "Int"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

class Contract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True, unique=True)
    status: str = Field(default="processing")
    
    # Campos que serão preenchidos pela IA
    contracting_party: Optional[str] = None
    contracted_party: Optional[str] = None
    contract_value: Optional[str] = None
    main_obligations: Optional[str] = None
    additional_data: Optional[str] = None
    termination_clause: Optional[str] = None