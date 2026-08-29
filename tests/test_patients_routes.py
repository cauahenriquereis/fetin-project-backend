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
    mock_patient.temperature = 37.5
    mock_patient.systolic_pressure = 120
    mock_patient.diastolic_pressure = 80
    mock_patient.heart_rate = 78
    mock_patient.oxygen_saturation = 97

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
                "created_at": "2026-08-25T10:00:00",
                "temperature": 37.5,
                "systolic_pressure": 120,
                "diastolic_pressure": 80,
                "heart_rate": 78,
                "oxygen_saturation": 97
            },
            "queue_position": 3,
            "waiting_time_minutes": 25,
            "priority_number": 100
        }
        mock_calc.assert_called_once_with(mock_patient, mock_session)

    finally:
        app.dependency_overrides.pop(get_calc_fn)

def test_register_patient_success(client, mock_session):
    patient_data = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.refresh.side_effect = fake_refresh

    response = client.post("/patients/register", json=patient_data)

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "John Doe"
    assert body["email"] == "john@example.com"
    assert body["status"] == "aguardando_sinais_vitais"
    assert body["urgency_level"] is None
    assert body["priority_number"] is None
    assert body["id"] == 1
    assert body["created_at"] == "2026-08-25T10:00:00"

    created_patient = mock_session.add.call_args[0][0]
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(created_patient)

def test_register_patient_with_no_email(client, mock_session):
    patient_data = {
        "full_name": "Jane Doe",
        "email": None,
        "age": 30,
        "symptoms": "dor no peito",
        "pain_level": 7
    }

    def fake_refresh(patient):
        patient.id = 1
        patient.created_at = datetime(2026, 8, 25, 10, 0, 0)

    mock_session.refresh.side_effect = fake_refresh

    response = client.post("/patients/register", json=patient_data)

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Jane Doe"
    assert body["email"] is None
    assert body["status"] == "aguardando_sinais_vitais"
    assert body["urgency_level"] is None
    assert body["priority_number"] is None

    mock_session.commit.assert_called_once()

VITALS_PAYLOAD = {
    "temperature": 37.5,
    "systolic_pressure": 120,
    "diastolic_pressure": 80,
    "heart_rate": 78,
    "oxygen_saturation": 97
}

def _make_patient(**overrides):
    patient = MagicMock()
    patient.id = 1
    patient.full_name = "John Doe"
    patient.email = "john@example.com"
    patient.age = 30
    patient.symptoms = "dor no peito"
    patient.pain_level = 7
    patient.status = "aguardando_sinais_vitais"
    patient.created_at = datetime(2026, 8, 25, 10, 0, 0)
    for key, value in overrides.items():
        setattr(patient, key, value)
    return patient

def test_update_vital_signs_not_found(client, mock_session):
    mock_session.query.return_value.filter.return_value.first.return_value = None

    response = client.patch("/patients/1/vitals", json=VITALS_PAYLOAD)

    assert response.status_code == 404
    assert response.json() == {"detail": "Paciente não encontrado"}

def test_update_vital_signs_success(client, mock_session):
    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient = _make_patient()

    mock_session.query.return_value.filter.return_value.first.return_value = patient
    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    try:
        response = client.patch("/patients/1/vitals", json=VITALS_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 100
        assert body["status"] == "aguardando"
        assert body["temperature"] == 37.5
        assert body["systolic_pressure"] == 120
        assert body["diastolic_pressure"] == 80
        assert body["heart_rate"] == 78
        assert body["oxygen_saturation"] == 97

        mock_analyze.assert_called_once_with(
            patient.symptoms, patient.pain_level, patient.age,
            37.5, 120, 80, 78, 97
        )
        mock_calc.assert_called_once_with(patient, mock_session)
        mock_email.assert_called_once_with("John Doe", "john@example.com", 3, 25)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(patient)

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_update_vital_signs_after_priority_number_199(client, mock_session):
    last_patient = MagicMock()
    last_patient.priority_number = 199

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient = _make_patient(full_name="Jane Doe", email="jane@example.com")

    mock_session.query.return_value.filter.return_value.first.return_value = patient
    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = last_patient

    try:
        response = client.patch("/patients/1/vitals", json=VITALS_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 100
        assert body["status"] == "aguardando"

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_update_vital_signs_after_priority_number_299(client, mock_session):
    last_patient = MagicMock()
    last_patient.priority_number = 299

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "média"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient = _make_patient(full_name="Jane Doe", email="jane@example.com")

    mock_session.query.return_value.filter.return_value.first.return_value = patient
    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = last_patient

    try:
        response = client.patch("/patients/1/vitals", json=VITALS_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["urgency_level"] == "média"
        assert body["priority_number"] == 200
        assert body["status"] == "aguardando"

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_update_vital_signs_with_existing_priority_number(client, mock_session):
    last_patient = MagicMock()
    last_patient.priority_number = 150

    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient = _make_patient(full_name="Jane Doe", email="jane@example.com")

    mock_session.query.return_value.filter.return_value.first.return_value = patient
    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = last_patient

    try:
        response = client.patch("/patients/1/vitals", json=VITALS_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 151
        assert body["status"] == "aguardando"

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)

def test_update_vital_signs_with_no_email(client, mock_session):
    mock_calc = MagicMock(return_value=(3, 25))
    mock_email = MagicMock()
    mock_analyze = AsyncMock(return_value={"urgency_level": "alta"})

    app.dependency_overrides[get_calc_fn] = lambda: mock_calc
    app.dependency_overrides[get_email_fn] = lambda: mock_email
    app.dependency_overrides[get_symptoms_analyze_fn] = lambda: mock_analyze

    patient = _make_patient(full_name="Jane Doe", email=None)

    mock_session.query.return_value.filter.return_value.first.return_value = patient
    mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    try:
        response = client.patch("/patients/1/vitals", json=VITALS_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["email"] is None
        assert body["urgency_level"] == "alta"
        assert body["priority_number"] == 100
        assert body["status"] == "aguardando"

        mock_calc.assert_not_called()
        mock_email.assert_not_called()
        mock_session.commit.assert_called_once()

    finally:
        app.dependency_overrides.pop(get_calc_fn)
        app.dependency_overrides.pop(get_email_fn)
        app.dependency_overrides.pop(get_symptoms_analyze_fn)