from sqlmodel import Session
from . import models, auth, schemas


# --- Funções de Usuário ---
def get_user_by_username(db: Session, username: str):
    """
    Busca o usuário no BD pelo seu nome
    """
    #Inicia a consulta na tabela "User" e filtra pelo username
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Cria o usuário no BD
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Funções de Contrato ---
def get_contract_by_filename(db: Session, filename: str):
    """
    Busca o contrato no BD pelo seu nome
    """
    return db.query(models.Contract).filter(models.Contract.filename == filename).first()

def create_contract(db: Session, filename: str):
    """
    Cria o contract no BD
    """
    db_contract = models.Contract(filename=filename, status="processing")
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def update_contract_with_data(db: Session, contract_id: int, data: schemas.ContractData):
    """
    Atualiza informações de algum contract
    """
    db_contract = db.get(models.Contract, contract_id)
    if db_contract:
        update_data = data.model_dump(exclude_unset=True)  # converte o objeto pydantic para um dict # exclude_unset quer dizer que
                                                           # apenas terá os itens requisitados pelo usuario no dict, para fazer apenas 
                                                           # a alteração neles
        for key, value in update_data.items():  # Aqui é feito de fato a att par cada item requisitado
            setattr(db_contract, key, value)  # aqui settamos os valores alterados
        db_contract.status = "completed"
        db.commit()
        db.refresh(db_contract)
    return db_contract

def update_contract_status(db: Session, contract_id: int, status: str):
    """
    Atualiza apenas o status do contrato
    """
    db_contract = db.get(models.Contract, contract_id)
    if db_contract:
        db_contract.status = status
        db.commit()
        db.refresh(db_contract)
    return db_contract