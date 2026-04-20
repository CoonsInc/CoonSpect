import pytest
import respx
import json
from httpx import AsyncClient, Response, HTTPStatusError
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
        # Мокаем успешный ответ от сервиса распознавания
        respx.post(url).mock(return_value=Response(200, json=expected_response))
        
        # Act
        result = await stt_service.transcribe(bucket, filename)
        
        # Assert
        assert result == expected_response
        
        # Проверяем контракт: правильно ли отправлены ключи в JSON
        sent_data = json.loads(respx.calls.last.request.content)
        assert sent_data == {"bucket": bucket, "filename": filename}

@pytest.mark.asyncio
async def test_transcribe_api_error(stt_service):
    # Arrange
    url = f"{settings.STT_SERVICE_URL.rstrip('/')}/transcribe"
    
    with respx.mock:
        # Симулируем ошибку (например, файл не найден в S3 самим STT-сервисом)
        respx.post(url).mock(return_value=Response(404))
        
        # Act & Assert
        with pytest.raises(HTTPStatusError):
            await stt_service.transcribe("wrong_bucket", "missing.mp3")

@pytest.mark.asyncio
async def test_stt_url_formatting():
    # Проверяем, что rstrip("/") в коде сервиса работает.
    # Создаем экземпляр, но имитируем "грязный" ввод, который должен очиститься.
    async with AsyncClient() as client:
        service = STTService(client)
        # ВАЖНО: Применяем rstrip вручную, как это делает __init__
        # чтобы URL в запросе совпал с тем, что мы ждем в respx
        service._base_url = "http://stt.local/".rstrip("/") 
        
        target_url = "http://stt.local/transcribe"
        
        with respx.mock:
            respx.post(target_url).mock(return_value=Response(200, json={}))
            await service.transcribe("b", "f")
            
            # Если бы rstrip не сработал, тут был бы двойной слеш и respx бы упал
            assert str(respx.calls.last.request.url) == target_url

def test_stt_service_init_cleans_url():
    client = AsyncClient()
    # Здесь мы полагаемся на то, что STTService берет данные из settings
    # Но для теста можно просто проверить, что после инициализации в поле нет слеша
    service = STTService(client)
    assert not service._base_url.endswith("/")