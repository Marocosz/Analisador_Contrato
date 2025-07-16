import os  # <--- ADICIONE ESTA LINHA
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
import shutil
import tempfile

from . import auth, crud, models, schemas, database, processing

models.SQLModel.metadata.create_all(bind=database.engine)

app = FastAPI(title="Contract Analyzer API")

# --- Endpoints de Autenticação e Usuários ---

@app.post("/users/", response_model=schemas.UserRead, tags=["Users"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_session)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já registrado")
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token, tags=["Users"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_session)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
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
    # A mágica acontece no `Depends(auth.get_current_user)`.
    # Se o token for inválido, o código nem chega a ser executado.
    return current_user


@app.post("/contracts/upload", response_model=models.Contract, tags=["Contracts"])
def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    if crud.get_contract_by_filename(db, filename=file.filename):
        raise HTTPException(status_code=400, detail="Um contrato com este nome de arquivo já existe.")

    # Salva o arquivo enviado em um local temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    db_contract = crud.create_contract(db, filename=file.filename)
    
    try:
        extracted_data = processing.analyze_contract_with_ai(tmp_path)
        updated_contract = crud.update_contract_with_data(db, db_contract.id, extracted_data)
        return updated_contract
    except Exception as e:
        crud.update_contract_status(db, db_contract.id, "failed")
        raise HTTPException(status_code=500, detail=f"Falha ao processar o contrato com a IA: {e}")
    finally:
        os.remove(tmp_path) # Garante que o arquivo temporário seja deletado