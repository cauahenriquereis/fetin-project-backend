from sqlalchemy.orm import sessionmaker
from models import db
from jose import jwt, JWTError
from config import DOCTOR_PASSWORD, ALGORITHM, oauth2_schema
from fastapi import HTTPException, Depends

SessionLocal = sessionmaker(bind=db)

def pegar_sessao():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def verify_token(token: str = Depends(oauth2_schema)):
    try:
        info_dictionary = jwt.decode(token, DOCTOR_PASSWORD, algorithms=[ALGORITHM])
        return info_dictionary
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido, verifique a validade do token")