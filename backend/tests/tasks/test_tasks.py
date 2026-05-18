import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.tasks.status import TaskStatus
from src.tasks.tasks import llm_step, run_audio_pipeline, save_step, stt_step


@pytest.mark.asyncio
async def test_stt_step_success(mock_stt_service):
    mock_stt_service.transcribe.return_value = {"text": "Hello world"}

    result = await stt_step.kiq("bucket", "file.mp3")
    res_value = (await result.wait_result()).return_value

    assert res_value["text"] == "Hello world"
    mock_stt_service.transcribe.assert_called_once_with("bucket", "file.mp3")


@pytest.mark.asyncio
async def test_llm_step_success(mock_llm_service):
    mock_llm_service.summarize.return_value = {"summary": "Short text"}

    result = await llm_step.kiq("Long text")
    res_value = (await result.wait_result()).return_value

    assert res_value == "Short text"
    mock_llm_service.summarize.assert_called_once_with("Long text")


@pytest.mark.asyncio
async def test_save_step_success(mock_lecture_crud):
    user_id = uuid4()
    lecture_id = uuid4()

    mock_lecture = MagicMock()
    mock_lecture.id = lecture_id
    mock_lecture_crud.create.return_value = mock_lecture

    result = await save_step.kiq(user_id, "name", "path", "text")
    res_value = (await result.wait_result()).return_value

    assert res_value == str(lecture_id)
    mock_lecture_crud.create.assert_called_once()


@pytest.mark.asyncio
async def test_full_pipeline_success(
    fake_redis, mock_s3_service, mock_stt_service, mock_llm_service, mock_lecture_crud
):
    task_id = "test_task_123"
    user_id = uuid4()
    lecture_id = uuid4()
    bucket = "test-bucket"
    filename = "audio.mp3"

    mock_s3_service.wait_object.return_value = None
    mock_stt_service.transcribe.return_value = {"text": "Original text"}
    mock_llm_service.summarize.return_value = {"summary": "Summarized text"}

    mock_lecture = MagicMock()
    mock_lecture.id = lecture_id
    mock_lecture_crud.create.return_value = mock_lecture

    handle = await run_audio_pipeline.kiq(task_id, user_id, bucket, filename)
    await handle.wait_result()

    redis_data = await fake_redis.get(task_id)
    assert redis_data is not None
    status_payload = json.loads(redis_data)

    assert status_payload["status"] == TaskStatus.FINISH
    assert status_payload["data"] == str(lecture_id)

    mock_stt_service.transcribe.assert_called_once()
    mock_llm_service.summarize.assert_called_once_with("Original text")
    mock_lecture_crud.create.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_error_handling(fake_redis, mock_s3_service):
    task_id = "error_task"
    mock_s3_service.wait_object.side_effect = Exception("S3 Connection Error")

    handle = await run_audio_pipeline.kiq(task_id, uuid4(), "b", "f")

    with pytest.raises(Exception) as exc:
        await (await handle.wait_result()).raise_for_error()

    assert "S3 Connection Error" in str(exc.value)

    redis_data = await fake_redis.get(task_id)
    assert redis_data is not None
    status_payload = json.loads(redis_data)
    assert TaskStatus(status_payload["status"]) == TaskStatus.ERROR
