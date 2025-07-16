from sqlmodel import create_engine, Session

# O nome do arquivo do nosso banco de dados SQLite
DATABASE_FILE = "database.db"
# A URL de conexão para o SQLite
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# O 'engine' é o ponto central de comunicação com o banco.
# 'connect_args' é necessário especificamente para SQLite para permitir seu uso com FastAPI.
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def get_session():
    """
    Função para prover uma sessão de banco de dados para os endpoints.
    """
    with Session(engine) as session:
        yield session