import json

import pytest
import respx
from httpx import AsyncClient, HTTPStatusError, Response

from src.services.stt import STTService
from src.settings import settings


@pytest.fixture
async def stt_service():
    async with AsyncClient() as client:
        yield STTService(client)


@pytest.mark.asyncio
async def test_transcribe_success(stt_service):
    # Arrange
    bucket = "lectures"
    filename = "audio_123.mp3"
    expected_response = {"text": "Результат распознавания речи"}

    url = f"{settings.STT_SERVICE_URL.rstrip('/')}/transcribe"

    with respx.mock:
        respx.post(url).mock(return_value=Response(200, json=expected_response))

        result = await stt_service.transcribe(bucket, filename)

        assert result == expected_response

        sent_data = json.loads(respx.calls.last.request.content)
        assert sent_data == {"bucket": bucket, "filename": filename}


@pytest.mark.asyncio
async def test_transcribe_api_error(stt_service):
    url = f"{settings.STT_SERVICE_URL.rstrip('/')}/transcribe"

    with respx.mock:
        respx.post(url).mock(return_value=Response(404))

        with pytest.raises(HTTPStatusError):
            await stt_service.transcribe("wrong_bucket", "missing.mp3")


@pytest.mark.asyncio
async def test_stt_url_formatting():
    async with AsyncClient() as client:
        service = STTService(client)
        service._base_url = "http://stt.local/".rstrip("/")

        target_url = "http://stt.local/transcribe"

        with respx.mock:
            respx.post(target_url).mock(return_value=Response(200, json={}))
            await service.transcribe("b", "f")

            assert str(respx.calls.last.request.url) == target_url


def test_stt_service_init_cleans_url():
    client = AsyncClient()
    service = STTService(client)
    assert not service._base_url.endswith("/")
