import os
import shutil
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from . import auth, crud, models, schemas, database, processing
from .database import engine  # Importamos o engine para o lifespan

# A função de ciclo de vida que cria as tabelas na inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando a aplicação...")
    models.SQLModel.metadata.create_all(bind=engine)  # Criando as tabelas (se não criadas)
    yield  # Linha de divisão (pausa e o próximo só acontece ao encerrar a aplicação)
    print("Finalizando a aplicação.")


# Inicialização do App e o lifespan como função de inicialização
app = FastAPI(title="Contract Analyzer API", lifespan=lifespan)

# Define as origens permitidas para CORS
origins = [
    "https://site-contratos-marcos.onrender.com",  # Servidor Render
    "http://localhost:8080"  # Servidor local
]

# Adiciona o middleware CORS para permitir requisições de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz para verificar se a API está online."""
    return {"status": "API is running!"}

# --- Endpoints de Autenticação e Usuários ---

@app.post("/users/", response_model=schemas.UserRead, tags=["Users"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_session)):
    """
    Função para criação de um novo usuário via API.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:  # Testa se o usuário já existe no banco de dados
        raise HTTPException(status_code=400, detail="Usuário já registrado")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token, tags=["Users"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Espera credenciais no formato OAuth2
    db: Session = Depends(database.get_session)
):
    """
    Endpoint para login de usuário e obtenção de um token de acesso JWT.
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        # Levanta exceção se o usuário não for encontrado ou a senha estiver incorreta
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Cria o token de acesso para o usuário autenticado
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Endpoint de teste para verificar a autenticação e retornar os dados do usuário logado.
    O `Depends(auth.get_current_user)` valida o token antes de executar a função.
    """
    return current_user


# --- Endpoint de Upload de Contrato (AGORA SÍNCRONO) ---
@app.post("/contracts/upload", response_model=models.Contract, tags=["Contracts"])
def upload_contract(
    file: UploadFile = File(...),  # Upload de arquivo obrigatório
    db: Session = Depends(database.get_session),  # Dependência de sessão do banco de dados
    current_user: models.User = Depends(auth.get_current_user)  # Verificação do token
):
    """
    Recebe um arquivo de contrato, salva-o temporariamente,
    executa a análise da IA de forma síncrona e retorna
    o contrato com todos os detalhes extraídos.
    """
    # Verificando nome do arquivo
    if crud.get_contract_by_filename(db, filename=file.filename):
        raise HTTPException(status_code=400, detail="Um contrato com este nome de arquivo já existe.")

    tmp_path = None  # Inicializa para garantir que o caminho do arquivo temporário esteja definido
    try:
        # Cria um arquivo único no sistema de arquivos temporário.
        # `delete=False` impede que o arquivo seja apagado automaticamente ao fechar.
        # `suffix` mantém a extensão original do arquivo.
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            shutil.copyfileobj(file.file, tmp)  # Copia o conteúdo do arquivo carregado para o arquivo temporário
            tmp_path = tmp.name  # Armazena o caminho completo do arquivo temporário para uso posterior

        # Criação do contrato no db
        db_contract = crud.create_contract(db, filename=file.filename)


        print(f"[IA] Iniciando análise do contrato ID {db_contract.id}")

        # Verificação de segurança
        if not os.path.exists(tmp_path):
            print(f"[IA] Erro: Arquivo temporário não encontrado em {tmp_path}")
            # Atualiza o status do contrato para falha
            crud.update_contract_status(db, db_contract.id, "failed")
            raise HTTPException(status_code=500, detail="Erro interno: Arquivo temporário para análise não encontrado.")

        # Chama a função de processamento da IA. E Salva os dados no formato do schemas.ContractData
        extracted_data: schemas.ContractData = processing.analyze_contract_with_ai(tmp_path)
        print(f"[IA] Extração concluída para contrato {db_contract.id}")

        # Atualização do contrato no db
        crud.update_contract_with_data(db, db_contract.id, extracted_data)

        # Atualiza o banco de dados para certeza dos dados atualizados
        db.refresh(db_contract)

    except Exception as e:
        # o status do contrato é definido como "failed".
        print(f"[Erro IA] Contrato ID {db_contract.id}: {e}")
        crud.update_contract_status(db, db_contract.id, "failed")
        raise HTTPException(status_code=500, detail=f"Erro na análise do contrato: {e}")
    finally:
        # Limpeza
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            print(f"[IA] Arquivo temporário removido: {tmp_path}")

    return db_contract


# --- Endpoints de Contrato (Busca, Listagem, Deleção) ---

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


@app.delete("/contracts/{contract_id}", response_model=models.Contract, tags=["Contracts"])
def remove_contract(
    contract_id: int,
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Deleta um contrato do banco de dados usando seu ID.
    """
    deleted_contract = crud.delete_contract(db, contract_id=contract_id)
    if deleted_contract is None:
        raise HTTPException(status_code=404, detail="Contrato não encontrado para deletar.")
    return deleted_contract