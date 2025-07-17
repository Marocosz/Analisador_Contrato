import pytest  # Framework de testes
import os
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel

from app.main import app
from app.database import get_session
from app import models

# Define o nome do arquivo do banco de dados de teste
TEST_DATABASE_FILE = "./test.db"
DATABASE_URL = f"sqlite:///{TEST_DATABASE_FILE}"

# Cria o 'engine' para o banco de teste
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Fixture que gerencia o ciclo de vida do banco de dados para CADA teste
# Fixtures são funções que fornecem recursos (como uma sessão de banco de dados ou um cliente de teste) para os testes
@pytest.fixture(name="session")
def session_fixture():
    # Garante que não há um banco de dados antigo antes de começar
    if os.path.exists(TEST_DATABASE_FILE):
        os.remove(TEST_DATABASE_FILE)

    # Cria todas as tabelas com base no model do app (já que ele foi importado)
    SQLModel.metadata.create_all(engine)
    
    # Abre e entrega a sessão para o teste - Usa with para fechar após o uso
    with Session(engine) as session:
        yield session  # o yield "pausa"
    
    # Após o teste terminar, fecha as conexões e apaga o arquivo do banco
    engine.dispose()
    if os.path.exists(TEST_DATABASE_FILE):
        os.remove(TEST_DATABASE_FILE)

# Fixture que cria o cliente de teste usando a sessão de teste
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():  # Função para retornar a sessão
        return session  

    # Aqui vamos sobrescrever o app (api) com a sessão que precisamos
    # Ou seja, quando a api tentar obter uma sessão atráves do get_session, em vez dela abrir o bd normal
    # abrirá o bd criado para os testes
    app.dependency_overrides[get_session] = get_session_override
    
    yield TestClient(app)  # Aqui é onde o cliente do pytest acontece

    app.dependency_overrides.clear()