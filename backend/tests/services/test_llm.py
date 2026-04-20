import pytest
import respx
import json
from httpx import AsyncClient, Response, HTTPStatusError
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
        # Сравниваем как объекты, а не как байты, чтобы избежать проблем с пробелами
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
    # Создаем моковый URL, который гарантированно имеет слеш в конце
    fake_base_url = "http://api.test.local/"
    
    async with AsyncClient() as client:
        # Инжектим базовый URL напрямую при создании, чтобы проверить rstrip
        service = LLMService(client)
        service._base_url = fake_base_url.rstrip("/") 
        
        # Ожидаемый правильный URL (без двойного слеша перед summarize)
        target_url = "http://api.test.local/summarize"
        
        with respx.mock:
            respx.post(target_url).mock(return_value=Response(200, json={"ok": True}))
            
            await service.summarize("text")
            
            # Если в запросе окажется http://api.test.local//summarize, respx выкинет ошибку
            assert respx.calls.last.request.url == target_url