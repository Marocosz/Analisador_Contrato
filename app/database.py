from sqlmodel import create_engine, Session
import os

# Se não encontrar, usa o valor padrão (nosso arquivo SQLite local).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")  # Online
#DATABASE_URL="sqlite:///database.db"  # Local

# O argumento 'connect_args' é um requisito apenas do SQLite.
# Este 'if' garante que só vamos usar esse argumento quando estivermos nos conectando a um banco SQLite.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# echo=False é melhor para produção para não poluir os logs
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

def get_session():
    """
    Função para prover uma sessão de banco de dados para os endpoints.
    """
    with Session(engine) as session:
        yield session