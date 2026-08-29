import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from google.genai import errors as genai_errors
from gemini_service import symptoms_analyze


@pytest.mark.asyncio
async def test_symptoms_analyze_success():
    mock_response = MagicMock()
    mock_response.text = '{"urgency_level": "alta"}'

    with patch("gemini_service.client.aio.models.generate_content", new=AsyncMock(return_value=mock_response)):
        resultado = await symptoms_analyze("dor no peito", 8, 30)

    assert resultado == {"urgency_level": "alta"}


@pytest.mark.asyncio
async def test_symptoms_analyze_client_error_returns_fallback():
    mock_error = genai_errors.ClientError(400, {"message": "bad request"})

    with patch("gemini_service.client.aio.models.generate_content", new=AsyncMock(side_effect=mock_error)):
        resultado = await symptoms_analyze("dor no peito", 8, 30)

    assert resultado == {"urgency_level": "média"}


@pytest.mark.asyncio
async def test_symptoms_analyze_invalid_json_returns_fallback():
    mock_response = MagicMock()
    mock_response.text = "isso não é json válido"

    with patch("gemini_service.client.aio.models.generate_content", new=AsyncMock(return_value=mock_response)):
        resultado = await symptoms_analyze("dor no peito", 8, 30)

    assert resultado == {"urgency_level": "média"}


@pytest.mark.asyncio
async def test_symptoms_analyze_server_error_exhausts_retries_returns_fallback():
    mock_error = genai_errors.ServerError(500, {"message": "server error"})

    with patch("gemini_service.client.aio.models.generate_content", new=AsyncMock(side_effect=mock_error)), \
         patch("gemini_service.asyncio.sleep", new=AsyncMock()) as mock_sleep:

        resultado = await symptoms_analyze("dor no peito", 8, 30)

    assert resultado == {"urgency_level": "média"}
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_symptoms_analyze_server_error_succeeds_on_retry():
    mock_success_response = MagicMock()
    mock_success_response.text = '{"urgency_level": "alta"}'
    mock_error = genai_errors.ServerError(500, {"message": "server error"})

    with patch(
        "gemini_service.client.aio.models.generate_content",
        new=AsyncMock(side_effect=[mock_error, mock_success_response])
    ), patch("gemini_service.asyncio.sleep", new=AsyncMock()) as mock_sleep:

        resultado = await symptoms_analyze("dor no peito", 8, 30)

    assert resultado == {"urgency_level": "alta"}
    assert mock_sleep.call_count == 1