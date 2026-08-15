import os 
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

# JWT signing algorithm (HS256)
ALGORITHM = os.getenv("ALGORITHM")

# Token expiration time — converted to int because os.getenv always returns string
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Shared doctor password for authentication
DOCTOR_PASSWORD = os.getenv("DOCTOR_PASSWORD")

# Gemini AI API key for triage analysis
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# OAuth2 scheme — defines the login endpoint for token generation
# Used by FastAPI to display the Authorize button in Swagger docs
oauth2_schema = OAuth2PasswordBearer(tokenUrl="doctor/login-form")

# Validate required environment variables
if not DOCTOR_PASSWORD:
    raise ValueError("DOCTOR_PASSWORD not found in .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

if not ALGORITHM:
    raise ValueError("ALGORITHM not found in .env")