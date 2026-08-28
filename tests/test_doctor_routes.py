from jose import jwt
from config import DOCTOR_PASSWORD, ALGORITHM
from doctor_routes import token_generator

def test_home(client):
    response = client.get("/doctor/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Você acessou a rota padrão de médicos", "autenticado":False}

def test_login_failed(client):
    response = client.post("/doctor/login", json={"senha": "wrong_password"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Senha incorreta"}

def test_login_success(client):
    response = client.post("/doctor/login", json={"senha": DOCTOR_PASSWORD})

    assert response.status_code == 200
    body = response.json()

    payload = jwt.decode(body["access_token"], DOCTOR_PASSWORD, algorithms=[ALGORITHM])
    assert payload["sub"] == "doctor"


def test_refresh_success(client):
    token = token_generator()

    response = client.get("/doctor/refresh", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "Bearer"    
