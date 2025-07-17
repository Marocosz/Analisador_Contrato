import os
import shutil
import tempfile
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from . import auth, crud, models, schemas, database, processing
from .database import engine # Importamos o engine para o lifespan

# A função de ciclo de vida que cria as tabelas na inicialização
@asynccontextmanager  # Decorator pra determinar gerenciador de eventos
async def lifespan(app: FastAPI):
    print("Iniciando a aplicação...")
    models.SQLModel.metadata.create_all(bind=engine)  # Criando as tabelas (Se não criadas)
    yield  # Linha de divisão (Pausa e o próximo só acontece ao encerrar a aplicação)
    print("Finalizando a aplicação.")


# Inicialização do App e o lifespan como função de inicialização 
app = FastAPI(title="Contract Analyzer API", lifespan=lifespan)

origins = [
    "http://localhost:8080",  # Servidor comum
    "https://site-contratos-marcos.onrender.com"  # Servidor render
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz para verificar se a API está online."""
    return {"status": "API is running!"}

# --- Endpoints de Autenticação e Usuários ---
# responde_model = UserRead para definição da estrutura
# Tags para documentação na categoria "Users"
@app.post("/users/", response_model=schemas.UserRead, tags=["Users"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_session)):
    """
    Função para criação do usuário pela API
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:  # Testa se já existe
        raise HTTPException(status_code=400, detail="Usuário já registrado")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token, tags=["Users"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # Faz com que o formato esperado seja as credencias OAuth2
    db: Session = Depends(database.get_session)):
    
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):  # Login não autorizado quase não bater a verificação de senha ou não existir o usuário
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint de teste para verificar a autenticação
@app.get("/users/me", response_model=schemas.UserRead, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    # O `Depends(auth.get_current_user)` faz a validação do token em relação ao usuário pelo seu username
    # Se o token for inválido, o código nem chega a ser executado.
    return current_user

# Task de background da analise
def process_contract_async(file_path: str, contract_id: int):

    db = next(database.get_session())  # Entrando no bd
    try:
        extracted_data = processing.analyze_contract_with_ai(file_path)  # Extrai as informações do contrato com a IA
        crud.update_contract_with_data(db, contract_id, extracted_data)  # Update das informações no BD
    except Exception as e:
        crud.update_contract_status(db, contract_id, "failed")
        print(f"[Erro IA] Contrato ID {contract_id}: {e}")  # Ou logging
    finally:
        os.remove(file_path)  # Apagando o arquivo temporário


@app.post("/contracts/upload", response_model=models.Contract, tags=["Contracts"])
def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),  # Upload de arquivo obrigatório
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(auth.get_current_user)):  # Verificação do token
    
    # Verificação de nome
    if crud.get_contract_by_filename(db, filename=file.filename):
        raise HTTPException(status_code=400, detail="Um contrato com este nome de arquivo já existe.")

    # Salva o arquivo enviado em um local temporário (mantem a extensão original)
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)  # Copia o conteudo do arquivo
        tmp_path = tmp.name
    
    db_contract = crud.create_contract(db, filename=file.filename)  # Cria no banco de dados
    
    # Inicia análise em segundo plano
    background_tasks.add_task(process_contract_async, tmp_path, db_contract.id)
    
    return db_contract
        

@app.get("/contracts/{contract_name}", response_model=models.Contract, tags=["Contracts"])
def get_contract_details(
    contract_name: str,
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Recupera os detalhes de um contrato específico pelo seu nome de arquivo.
    """
    db_contract = crud.get_contract_by_filename(db, filename=contract_name)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    return db_contract


@app.get("/contracts/list/filenames", response_model=list[str], tags=["Contracts"])
def get_contract_filenames(
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Recupera uma lista com os nomes de todos os contratos existentes.
    """
    filenames = crud.get_all_contract_filenames(db)
    return filenames