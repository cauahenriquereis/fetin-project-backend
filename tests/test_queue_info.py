from unittest.mock import MagicMock
from queue_routes import calculate_queue_info  


def test_calculate_queue_info_alta_urgencia(mock_session):
    mock_session.query.return_value.filter.return_value.count.return_value = 0

    patient = MagicMock()
    patient.priority_number = 150

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 1
    assert waiting_time == 0

def test_calculate_queue_info_media_urgencia(mock_session):
    mock_session.query.return_value.filter.return_value.count.return_value = 0

    patient = MagicMock()
    patient.priority_number = 250

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 1
    assert waiting_time == 0

def test_calculate_queue_info_baixa_urgencia(mock_session):
    mock_session.query.return_value.filter.return_value.count.return_value = 0

    patient = MagicMock()
    patient.priority_number = 350

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 1
    assert waiting_time == 0    

def test_calculate_queue_info_boundary_high_urgency(mock_session):
    mock_session.query.return_value.filter.return_value.count.side_effect = [7, 2, 1]

    patient = MagicMock()
    patient.priority_number = 199

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 8
    assert waiting_time == 70

def test_calculate_queue_info_boundary_medium_urgency(mock_session):
    mock_session.query.return_value.filter.return_value.count.side_effect = [5, 3, 2]

    patient = MagicMock()
    patient.priority_number = 299

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 9
    assert waiting_time == 71 

def test_calculate_queue_info_with_patients_ahead_high(mock_session):
    mock_session.query.return_value.filter.return_value.count.side_effect = [3, 0, 0]

    patient = MagicMock()
    patient.priority_number = 150

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 4
    assert waiting_time == 30   

def test_calculate_queue_info_with_patients_ahead_medium(mock_session):
    mock_session.query.return_value.filter.return_value.count.side_effect = [3, 4, 0]

    patient = MagicMock()
    patient.priority_number = 250

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 8
    assert waiting_time == 58

def test_calculate_queue_info_with_patients_ahead_low(mock_session):
    mock_session.query.return_value.filter.return_value.count.side_effect = [3, 4, 7]

    patient = MagicMock()
    patient.priority_number = 350

    queue_position, waiting_time = calculate_queue_info(patient, mock_session)

    assert queue_position == 15
    assert waiting_time == 93
     