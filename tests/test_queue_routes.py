from unittest.mock import MagicMock


def test_get_ordered_queue_returns_empty_list(client, mock_session):
    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    response = client.get("/queue/status")

    assert response.status_code == 200
    assert response.json() == []

from datetime import datetime

def test_get_ordered_queue_returns_patients(client, mock_session):
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