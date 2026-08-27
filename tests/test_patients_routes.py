from datetime import datetime
from unittest.mock import MagicMock
from main import app
from queue_routes import get_calc_fn


def test_get_patient_not_found(client, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None

    response = client.get("/patients/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Paciente não encontrado"}

def test_get_patient_not_waiting(client, mock_session):
    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.full_name = "John Doe"
    mock_patient.email = "john@example.com"
    mock_patient.age = 30
    mock_patient.symptoms = "dor no peito"
    mock_patient.pain_level = 7
    mock_patient.urgency_level = "alta"
    mock_patient.priority_number = 100
    mock_patient.status = "atendido"
    mock_patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.query.return_value.filter.return_value.first.return_value = mock_patient

    response = client.get("/patients/1")

    assert response.status_code == 400
    assert response.json() == {"detail": f"Paciente não está na fila. Status atual: {mock_patient.status}"}

def test_get_patient_success(client, mock_session):

    mock_calc = MagicMock(return_value=(3, 25))

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc

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

    try:
        response = client.get("/patients/1")

        assert response.status_code == 200
        assert response.json() == {
            "patient": {
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
            },
            "queue_position": 3,
            "waiting_time_minutes": 25,
            "priority_number": 100
        }
        mock_calc.assert_called_once_with(mock_patient, mock_session)

    finally:
        app.dependency_overrides.pop(get_calc_fn)    
