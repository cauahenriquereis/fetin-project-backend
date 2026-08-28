from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from main import app
from queue_routes import get_calc_fn, get_email_fn
from patients_routes import get_symptoms_analyze_fn
from tests.conftest import mock_session

def test_home(client):
    response = client.get("/patients/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Você acessou a rota padrão de pacientes", "autenticado": False}


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


def test_register_patient_success(client, mock_session):
    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient_data = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.refresh.side_effect = fake_refresh

    try:
        response = client.post("/patients/register", json=patient_data)

        assert response.status_code == 200
        body = response.json()
        assert body["full_name"] == "John Doe"
        assert body["email"] == "john@example.com"
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 100
        assert body["status"] == "aguardando"
        assert body["id"] == 1
        assert body["created_at"] == "2026-08-25T10:00:00"

        created_patient = mock_session.add.call_args[0][0]

        mock_calc.assert_called_once_with(created_patient, mock_session)
        mock_email.assert_called_once_with("John Doe", "john@example.com", 3, 25)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(created_patient)

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_register_patient_after_priority_number_199(client, mock_session):

    mock_patient = MagicMock()
    mock_patient.priority_number = 199

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient_data = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_patient

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.refresh.side_effect = fake_refresh

    try:
        response = client.post("/patients/register", json=patient_data)

        assert response.status_code == 200
        body = response.json()
        assert body["full_name"] == "Jane Doe"
        assert body["email"] == "jane@example.com"
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 100
        assert body["status"] == "aguardando"
        assert body["id"] == 1
        assert body["created_at"] == "2026-08-25T10:00:00"

        created_patient = mock_session.add.call_args[0][0]

        mock_calc.assert_called_once_with(created_patient, mock_session)
        mock_email.assert_called_once_with("Jane Doe", "jane@example.com", 3, 25)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(created_patient)

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_register_patient_after_priority_number_299(client, mock_session):

    mock_patient = MagicMock()
    mock_patient.priority_number = 299

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "média"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient_data = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_patient

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.refresh.side_effect = fake_refresh

    try:
        response = client.post("/patients/register", json=patient_data)

        assert response.status_code == 200
        body = response.json()
        assert body["full_name"] == "Jane Doe"
        assert body["email"] == "jane@example.com"
        assert body["urgency_level"] == "média"
        assert body["priority_number"] == 200
        assert body["status"] == "aguardando"
        assert body["id"] == 1
        assert body["created_at"] == "2026-08-25T10:00:00"

        created_patient = mock_session.add.call_args[0][0]

        mock_calc.assert_called_once_with(created_patient, mock_session)
        mock_email.assert_called_once_with("Jane Doe", "jane@example.com", 3, 25)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(created_patient)

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_register_patient_with_existing_priority_number(client, mock_session):

    mock_patient = MagicMock()
    mock_patient.priority_number = 150

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient_data = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_patient

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)
    mock_session.refresh.side_effect = fake_refresh

    try:
        response = client.post("/patients/register", json=patient_data)

        assert response.status_code == 200
        body = response.json()
        assert body["full_name"] == "Jane Doe"
        assert body["email"] == "jane@example.com"
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 151
        assert body["status"] == "aguardando"
        assert body["id"] == 1
        assert body["created_at"] == "2026-08-25T10:00:00"

        created_patient = mock_session.add.call_args[0][0]

        mock_calc.assert_called_once_with(created_patient, mock_session)
        mock_email.assert_called_once_with("Jane Doe", "jane@example.com", 3, 25)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(created_patient)
        
    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_register_patient_with_no_email(client, mock_session):

    mock_patient = MagicMock()
    mock_patient.priority_number = 150

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient_data = {
        "full_name": "Jane Doe",
        "email": None,
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_patient

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)
    mock_session.refresh.side_effect = fake_refresh

    try:
        response = client.post("/patients/register", json=patient_data)

        assert response.status_code == 200
        body = response.json()
        assert body["full_name"] == "Jane Doe"
        assert body["email"] is None
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 151
        assert body["status"] == "aguardando"
        assert body["id"] == 1
        assert body["created_at"] == "2026-08-25T10:00:00"

        created_patient = mock_session.add.call_args[0][0]

        mock_calc.assert_not_called()
        mock_email.assert_not_called()  
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(created_patient)
        
    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)