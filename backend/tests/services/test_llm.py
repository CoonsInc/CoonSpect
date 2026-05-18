import json

import pytest
import respx
from httpx import AsyncClient, HTTPStatusError, Response

from src.services.llm import LLMService
from src.settings import settings


@pytest.fixture
async def llm_service():
    async with AsyncClient() as client:
        yield LLMService(client)


@pytest.mark.asyncio
async def test_summarize_success(llm_service):
    input_text = "Длинный текст для суммаризации"
    expected_response = {"summary": "Краткое содержание"}
    url = f"{settings.LLM_SERVICE_URL.rstrip('/')}/summarize"

    with respx.mock:
        respx.post(url).mock(return_value=Response(200, json=expected_response))

        result = await llm_service.summarize(input_text)

        assert result == expected_response
        sent_data = json.loads(respx.calls.last.request.content)
        assert sent_data == {"text": input_text}


@pytest.mark.asyncio
async def test_summarize_api_error(llm_service):
    url = f"{settings.LLM_SERVICE_URL.rstrip('/')}/summarize"

    with respx.mock:
        respx.post(url).mock(return_value=Response(500))

        with pytest.raises(HTTPStatusError):
            await llm_service.summarize("test")


@pytest.mark.asyncio
async def test_url_formatting_with_trailing_slash():
    fake_base_url = "http://api.test.local/"

    async with AsyncClient() as client:
        service = LLMService(client)
        service._base_url = fake_base_url.rstrip("/")
        target_url = "http://api.test.local/summarize"

        with respx.mock:
            respx.post(target_url).mock(return_value=Response(200, json={"ok": True}))

            await service.summarize("text")
            assert respx.calls.last.request.url == target_url
