from sqlmodel import Session
from . import models, auth, schemas

# --- Funções de Usuário ---

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Funções de Contrato ---

def get_contract_by_filename(db: Session, filename: str):
    return db.query(models.Contract).filter(models.Contract.filename == filename).first()

def create_contract(db: Session, filename: str):
    db_contract = models.Contract(filename=filename, status="processing")
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def update_contract_with_data(db: Session, contract_id: int, data: schemas.ContractData):
    db_contract = db.get(models.Contract, contract_id)
    if db_contract:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contract, key, value)
        db_contract.status = "completed"
        db.commit()
        db.refresh(db_contract)
    return db_contract

def update_contract_status(db: Session, contract_id: int, status: str):
    db_contract = db.get(models.Contract, contract_id)
    if db_contract:
        db_contract.status = status
        db.commit()
        db.refresh(db_contract)
    return db_contract