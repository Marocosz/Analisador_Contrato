import os
from datetime import datetime, timedelta, timezone 
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from . import database, models


# --- Configuração de Segurança ---
SECRET_KEY = os.getenv("JWT_KEY")  # Key para proteção do sistema de criação de token
ALGORITHM = "HS256"  # Algoritmo de criação dos tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# Contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 que aponta para o nosso futuro endpoint de login (Serve para extrair o token do cabeçalho)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# Função para verificação do hash com a senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Usando o pwd para criar o hash da senha
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Criando o token de acesso de acordo com o tempo
def create_access_token(data: dict):
    """
    Aqui o token se vincula com o determinado username na hora da criação
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Função de defesa dos endpoints/verificação do token
# OBS: O "Depends" é o gerenciador de dependencia
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Verificação do Token (ler o payload dele e ver se existe o vinculo com o username)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    #Verificação de usuário com o banco de dados
    statement = select(models.User).where(models.User.username == username)
    user = db.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user