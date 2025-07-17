from fastapi.testclient import TestClient
from app import schemas

# Teste 1: Rotas públicas básicas
def test_read_root(client: TestClient):
    """Testa se a rota principal está online."""
    response = client.get("/")
    assert response.status_code == 200
    # CORREÇÃO: Agora o teste verifica a mensagem exata que a API retorna
    assert response.json()["status"] == "API is running!"

def test_create_user(client: TestClient):
    """Testa se a criação de um usuário funciona e retorna os dados corretos."""
    response = client.post(
        "/users/",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "hashed_password" not in data # Garante que a senha não é exposta

# Teste 2: Fluxo de Autenticação Completo
def test_login_for_access_token(client: TestClient):
    """Testa se, após criar um usuário, conseguimos logar e receber um token."""
    # Primeiro, cria um usuário para o teste
    client.post("/users/", json={"username": "logintest", "password": "password123"})

    # Tenta fazer o login com as mesmas credenciais
    response = client.post(
        "/login",
        data={"username": "logintest", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# Teste 3: Acesso a Rotas Protegidas
def test_fail_to_access_protected_route_without_token(client: TestClient):
    """Testa se a API bloqueia o acesso a uma rota protegida sem um token."""
    response = client.get("/contracts/list/filenames")
    assert response.status_code == 401 # Unauthorized

def test_access_protected_route_with_token(client: TestClient):
    """Testa o acesso a uma rota protegida usando um token válido."""
    # Cria usuário e obtém o token
    client.post("/users/", json={"username": "authuser", "password": "password123"})
    login_response = client.post("/login", data={"username": "authuser", "password": "password123"})
    token = login_response.json()["access_token"]

    # Usa o token para fazer a requisição
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/contracts/list/filenames", headers=headers)
    
    assert response.status_code == 200
    # Como o banco de dados está limpo, a resposta deve ser uma lista vazia
    assert response.json() == []

# Teste 4: Testando o Upload com "Mock" da IA
def test_upload_contract_with_mocking(client: TestClient, monkeypatch):
    """
    Testa o endpoint de upload substituindo a chamada à IA por uma função falsa.
    Isso torna o teste rápido, gratuito e previsível.
    """
    # Cria usuário e obtém o token
    client.post("/users/", json={"username": "uploaduser", "password": "password123"})
    login_response = client.post("/login", data={"username": "uploaduser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Define uma função falsa que imita a resposta da IA
    def fake_ai_analysis(file_path: str) -> schemas.ContractData:
        return schemas.ContractData(
            contracting_party="Empresa Teste SA",
            contracted_party="Fornecedor Mock",
            contract_value="R$ 50.000,00",
            main_obligations="Entregar o software.",
            additional_data="Vigência de 12 meses.",
            termination_clause="Multa de 10%."
        )

    # 2. Usa o 'monkeypatch' do pytest para substituir a função real pela nossa função falsa
    monkeypatch.setattr("app.processing.analyze_contract_with_ai", fake_ai_analysis)

    # 3. Executa o upload. O arquivo em si não importa, pois a análise será a falsa.
    file_content = "Este é um conteúdo de um pdf falso.".encode("utf-8")
    files = {"file": ("mock_contract.pdf", file_content, "application/pdf")}
    response = client.post("/contracts/upload", headers=headers, files=files)

    # 4. Verifica os resultados
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "mock_contract.pdf"
    assert data["status"] == "completed"
    assert data["contracting_party"] == "Empresa Teste SA" # Verifica se os dados do mock estão presentes