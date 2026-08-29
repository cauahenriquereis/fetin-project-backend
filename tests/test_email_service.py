from unittest.mock import patch
from email_service import send_queue_update_email


def test_send_queue_update_email_failure(caplog):
    with patch("email_service.resend.Emails.send", side_effect=Exception("Falha simulada no envio")):
        send_queue_update_email(
            patient_name="John Doe",
            patient_email="john.doe@example.com",
            queue_position=5,
            waiting_time=10
        )
    assert caplog.records[0].levelname == "ERROR"


def test_send_queue_update_email_success():
    with patch("email_service.resend.Emails.send") as mock_send:
        send_queue_update_email(
            patient_name="Jane Doe",
            patient_email="jane.doe@example.com",
            queue_position=3,
            waiting_time=5
        )
    call_args = mock_send.call_args[0][0]
    assert call_args["to"] == "jane.doe@example.com"
    assert "Jane Doe" in call_args["html"]
    assert "3º" in call_args["html"]    
    mock_send.assert_called_once()