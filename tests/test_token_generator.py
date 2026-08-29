from datetime import datetime, timezone, timedelta
from jose import jwt
from config import DOCTOR_PASSWORD, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from doctor_routes import token_generator


def test_token_generator_default_duration():
    token = token_generator()

    payload = jwt.decode(token, DOCTOR_PASSWORD, algorithms=[ALGORITHM])

    assert payload["sub"] == "doctor"

    expiration = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    diff = abs((expiration - expected_expiration).total_seconds())
    assert diff < 5


def test_token_generator_refresh_duration():
    token = token_generator(token_duration=timedelta(days=7))

    payload = jwt.decode(token, DOCTOR_PASSWORD, algorithms=[ALGORITHM])

    assert payload["sub"] == "doctor"

    expiration = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_expiration = datetime.now(timezone.utc) + timedelta(days=7)

    diff = abs((expiration - expected_expiration).total_seconds())
    assert diff < 5  