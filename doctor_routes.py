from fastapi import APIRouter, Depends, HTTPException
from schemas import LoginRequest 
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_schema, DOCTOR_PASSWORD
from dependencies import verify_token
from fastapi.security import OAuth2PasswordRequestForm

# Generates a JWT token with configurable duration
# Default: 30 minutes (access token)
# Can be overridden: 7 days (refresh token)
def token_generator(token_duration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + token_duration
    info_dictionary = {"sub": "doctor", "exp": expiration_date}
    encoded_jwt = jwt.encode(info_dictionary, DOCTOR_PASSWORD, ALGORITHM)
    return encoded_jwt

doctor_router = APIRouter(prefix="/doctor", tags = ["doctor"])

@doctor_router.get("/")
async def home():
    return{"mensagem": "Você acessou a rota padrão de médicos", "autenticado":False}

@doctor_router.post("/login")
async def login(dados: LoginRequest):
    # JSON login — used by the frontend
    # Returns both access token (30 min) and refresh token (7 days)
    if dados.senha == DOCTOR_PASSWORD:
        access_token = token_generator()
        refresh_token = token_generator(token_duration=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    else:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
@doctor_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends()):
     # Form login — used by the Swagger UI Authorize button
    # Returns only access token (Swagger does not support refresh tokens)
    if dados_formulario.password == DOCTOR_PASSWORD:
        access_token = token_generator()
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    else:
        raise HTTPException(status_code=401, detail="Senha incorreta")


@doctor_router.get("/refresh")
async def use_refresh_token(token: str = Depends(oauth2_schema)):
    # Validates the refresh token and returns a new access token
    # Used when the access token expires after 30 minutes
    verify_token(token)
    new_access_token = token_generator()
    return {
        "access_token": new_access_token,
        "token_type": "Bearer"
    }
