import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.s3 import S3Service

@pytest.fixture
def mock_s3_client():
    # Типизация aiobotocore требует AsyncMock для асинхронных вызовов
    return AsyncMock()

@pytest.fixture
def s3_service(mock_s3_client):
    return S3Service(s3_client=mock_s3_client)

@pytest.mark.asyncio
async def test_wait_object_calls_waiter(s3_service, mock_s3_client):
    # Arrange
    mock_waiter = AsyncMock()
    # get_waiter — синхронный метод у клиента
    mock_s3_client.get_waiter = MagicMock(return_value=mock_waiter)
    
    # Act
    await s3_service.wait_object("test-bucket", "test-key")
    
    # Assert
    mock_s3_client.get_waiter.assert_called_once_with("object_exists")
    mock_waiter.wait.assert_called_once_with(Bucket="test-bucket", Key="test-key", WaiterConfig={'Delay': 5, 'MaxAttempts': 20})

@pytest.mark.asyncio
async def test_get_download_url(s3_service, mock_s3_client):
    bucket, key = "my-bucket", "audio.mp3"
    mock_s3_client.generate_presigned_url.return_value = "https://ok.com"
    
    url = await s3_service.get_download_url(bucket, key, expiration=60)
    
    assert url == "https://ok.com"
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=60
    )

@pytest.mark.asyncio
async def test_get_upload_url_success(s3_service, mock_s3_client):
    # Arrange
    bucket, key = "my-bucket", "upload.mp3"
    content_type = "audio/mpeg"
    expected_url = "https://s3.amazon.com/presigned-put"
    mock_s3_client.generate_presigned_url.return_value = expected_url
    
    # Act
    url = await s3_service.get_upload_url(bucket, key, content_type, expiration=1800)
    
    # Assert
    assert url == expected_url
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        'put_object',
        Params={
            'Bucket': bucket, 
            'Key': key,
            'ContentType': content_type
        },
        ExpiresIn=1800
    )

@pytest.mark.asyncio
async def test_delete_object_success(s3_service, mock_s3_client):
    # Arrange
    bucket, key = "trash-bucket", "old-file.txt"
    
    # Act
    await s3_service.delete(bucket, key)
    
    # Assert
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket=bucket, 
        Key=key
    )

@pytest.mark.asyncio
async def test_delete_object_error(s3_service, mock_s3_client):
    # Проверка, что исключения пробрасываются выше
    mock_s3_client.delete_object.side_effect = Exception("S3 Connection Error")
    
    with pytest.raises(Exception) as exc:
        await s3_service.delete("b", "k")
    
    assert str(exc.value) == "S3 Connection Error"