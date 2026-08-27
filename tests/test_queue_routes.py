from unittest.mock import MagicMock
from datetime import datetime
from queue_routes import get_calc_fn, get_email_fn
from main import app

from tests.conftest import mock_session


def test_home_route(client):
    response = client.get("/queue")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Você acessou a rota padrão de filas", "autenticado": True}

def test_get_ordered_queue_returns_empty_list(client, mock_session):
    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    response = client.get("/queue/status")

    assert response.status_code == 200
    assert response.json() == []

def test_get_ordered_queue_returns_single_patient(client, mock_session):
    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"
    mock_patient.email = "john@example.com"
    mock_patient.age = 30
    mock_patient.symptoms = "dor no peito"
    mock_patient.pain_level = 7
    mock_patient.urgency_level = "alta"
    mock_patient.priority_number = 100
    mock_patient.status = "aguardando"
    mock_patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_patient]

    response = client.get("/queue/status")

    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7,
        "urgency_level": "alta",
        "priority_number": 100,
        "status": "aguardando",
        "created_at": "2026-08-25T10:00:00"
    }]   


def test_get_ordered_queue_returns_multiple_patients(client, mock_session):
    mock_patient_alta = MagicMock()
    mock_patient_alta.id = 1
    mock_patient_alta.full_name = "John Doe"
    mock_patient_alta.email = "john@example.com"
    mock_patient_alta.age = 30
    mock_patient_alta.symptoms = "dor no peito"
    mock_patient_alta.pain_level = 7
    mock_patient_alta.urgency_level = "alta"
    mock_patient_alta.priority_number = 100
    mock_patient_alta.status = "aguardando"
    mock_patient_alta.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_patient_media = MagicMock()
    mock_patient_media.id = 2
    mock_patient_media.full_name = "Jane Smith"
    mock_patient_media.email = "jane@example.com"
    mock_patient_media.age = 25
    mock_patient_media.symptoms = "dor de cabeça"
    mock_patient_media.pain_level = 5
    mock_patient_media.urgency_level = "média"
    mock_patient_media.priority_number = 200
    mock_patient_media.status = "aguardando"
    mock_patient_media.created_at = datetime(2026, 8, 25, 11, 0, 0)

    mock_patient_baixa = MagicMock()
    mock_patient_baixa.id = 3
    mock_patient_baixa.full_name = "Carlos Lima"
    mock_patient_baixa.email = "carlos@example.com"
    mock_patient_baixa.age = 40
    mock_patient_baixa.symptoms = "dor muscular leve"
    mock_patient_baixa.pain_level = 2
    mock_patient_baixa.urgency_level = "baixa"
    mock_patient_baixa.priority_number = 300
    mock_patient_baixa.status = "aguardando"
    mock_patient_baixa.created_at = datetime(2026, 8, 25, 12, 0, 0)

    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_patient_alta, mock_patient_media, mock_patient_baixa]

    response = client.get("/queue/status")

    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7,
        "urgency_level": "alta",
        "priority_number": 100,
        "status": "aguardando",
        "created_at": "2026-08-25T10:00:00"
    }, {
        "id": 2,
        "full_name": "Jane Smith",
        "email": "jane@example.com",
        "age": 25,
        "symptoms": "dor de cabeça",
        "pain_level": 5,
        "urgency_level": "média",
        "priority_number": 200,
        "status": "aguardando",
        "created_at": "2026-08-25T11:00:00"
    }, {
        "id": 3,
        "full_name": "Carlos Lima",
        "email": "carlos@example.com",
        "age": 40,
        "symptoms": "dor muscular leve",
        "pain_level": 2,
        "urgency_level": "baixa",
        "priority_number": 300,
        "status": "aguardando",
        "created_at": "2026-08-25T12:00:00"
    }]     

def test_get_next_patient_returns_patient(client, mock_session):
    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"
    mock_patient.email = "john@example.com"
    mock_patient.age = 30
    mock_patient.symptoms = "dor no peito"
    mock_patient.pain_level = 7
    mock_patient.urgency_level = "alta"
    mock_patient.priority_number = 100
    mock_patient.status = "aguardando"
    mock_patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_patient

    response = client.get("/queue/next/")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7,
        "urgency_level": "alta",
        "priority_number": 100,
        "status": "aguardando",
        "created_at": "2026-08-25T10:00:00"
        }
    
def test_get_next_patient_returns_404(client, mock_session):

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    response = client.get("/queue/next/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Não há pacientes aguardando atendimento"}

def test_get_patient_status_returns_patient(client, mock_session):
    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"
    mock_patient.email = "john@example.com"
    mock_patient.age = 30
    mock_patient.symptoms = "dor no peito"
    mock_patient.pain_level = 7
    mock_patient.urgency_level = "alta"
    mock_patient.priority_number = 100
    mock_patient.status = "aguardando"
    mock_patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.query.return_value.filter.return_value.first.return_value = mock_patient

    response = client.get("/queue/status/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7,
        "urgency_level": "alta",
        "priority_number": 100,
        "status": "aguardando",
        "created_at": "2026-08-25T10:00:00"
    }

def test_get_patient_status_returns_404(client, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None

    response = client.get("/queue/status/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Paciente não encontrado"}    

def test_remove_patient_from_queue(client, mock_session):
    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"

    mock_session.query.return_value.filter.return_value.first.return_value = mock_patient

    response = client.delete("/queue/1")

    assert response.status_code == 200
    assert response.json() == {"mensagem": f"Paciente {mock_patient.full_name} removido da fila"}

    mock_session.delete.assert_called_once_with(mock_patient)
    mock_session.commit.assert_called_once()

def test_remove_patient_from_queue_returns_404(client, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None

    response = client.delete("/queue/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Paciente não encontrado"}

def test_update_patient_status_returns_404(client, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None

    response = client.patch("/queue/999/status", json={"new_status": "em atendimento"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Paciente não encontrado"}

def test_update_patient_status_invalid_status(client, mock_session):

    mock_patient = MagicMock()

    mock_session.query.return_value.filter.return_value.first.return_value = mock_patient

    response = client.patch("/queue/1/status", json={"new_status": "atendimento inválido"})

    assert response.status_code == 422

def test_update_patient_status_em_atendimento(client, mock_session):
    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"
    mock_patient.email = "john@example.com"
    mock_patient.age = 30
    mock_patient.symptoms = "dor no peito"
    mock_patient.pain_level = 7
    mock_patient.urgency_level = "alta"
    mock_patient.priority_number = 100
    mock_patient.status = "aguardando"
    mock_patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.query.return_value.filter.return_value.first.return_value = mock_patient

    response = client.patch("/queue/1/status", json={"new_status": "em atendimento"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7,
        "urgency_level": "alta",
        "priority_number": 100,
        "status": "em atendimento",
        "created_at": "2026-08-25T10:00:00"
    }    
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_patient) 

def test_update_patient_status_atendido(client, mock_session):
    mock_calc = MagicMock(return_value=(2, 15))
    mock_email = MagicMock()

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email

    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"
    mock_patient.email = "john@example.com"
    mock_patient.age = 30
    mock_patient.symptoms = "dor no peito"
    mock_patient.pain_level = 7
    mock_patient.urgency_level = "alta"
    mock_patient.priority_number = 100
    mock_patient.status = "aguardando"
    mock_patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_patient_com_email = MagicMock()
    mock_patient_com_email.full_name = "Maria Silva"
    mock_patient_com_email.email = "maria@example.com"

    mock_session.query.return_value.filter.return_value.first.return_value = mock_patient
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_patient_com_email]

    try:
        response = client.patch("/queue/1/status", json={"new_status": "atendido"}) 

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "full_name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "symptoms": "dor no peito",
            "pain_level": 7,
            "urgency_level": "alta",
            "priority_number": 100,
            "status": "atendido",
            "created_at": "2026-08-25T10:00:00"
            }    
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_patient)    
        
        mock_calc.assert_called_once_with(mock_patient_com_email, mock_session)
        mock_email.assert_called_once_with("Maria Silva", "maria@example.com", 2, 15)

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
