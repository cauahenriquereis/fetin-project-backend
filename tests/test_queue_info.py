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
