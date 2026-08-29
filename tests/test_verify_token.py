import pytest
from dependencies import verify_token
from fastapi import HTTPException
from doctor_routes import token_generator

def test_verify_token_invalid_token():
    invalid_token = "invalid.token.value"

    with pytest.raises(HTTPException) as exc_info:
        verify_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido, verifique a validade do token"

def test_verify_token_valid_token():
    valid_token = token_generator()
 
    result = verify_token(valid_token)

    assert result["sub"] == "doctor"