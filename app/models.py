from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
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