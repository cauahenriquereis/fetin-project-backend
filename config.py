import os 
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

DOCTOR_PASSWORD = os.getenv("DOCTOR_PASSWORD")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="doctor/login-form")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES not found in .env")

if not DOCTOR_PASSWORD:
    raise ValueError("DOCTOR_PASSWORD not found in .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

if not ALGORITHM:
    raise ValueError("ALGORITHM not found in .env")

if not RESEND_API_KEY:
    raise ValueError("RESEND_API_KEY not found in .env")