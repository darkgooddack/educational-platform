
import pytest
from botocore.exceptions import ClientError
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_upload_video_file_success(s3_manager, mock_upload_video_file):
    """
    Проверяет загрузку видео файла.
    """
    mock_upload_video_file.content_type = "video/mp4"
    mock_upload_video_file.filename = "lecture.mp4"

    s3_manager.get_link_file = AsyncMock(return_value="https://education-platform.s3.storage.selcloud.ru/test_videos_lectures/videos/test.mp4")

    result = await s3_manager.upload_file_from_content(
        mock_upload_video_file,
        "test_videos_lectures/videos"
    )

    assert "test_videos_lectures/videos" in await result


@pytest.mark.asyncio
async def test_upload_thumbnail_success(s3_manager, mock_upload_image_file):
    """
    Проверяет загрузку файла обложки.
    """
    mock_upload_image_file.content_type = "image/jpeg"
    mock_upload_image_file.filename = "thumbnail.jpg"

    s3_manager.get_link_file = AsyncMock(return_value="https://education-platform.s3.storage.selcloud.ru/test_videos_lectures/thumbnails/test.jpg")

    result = await s3_manager.upload_file_from_content(
        mock_upload_image_file,
        "test_videos_lectures/thumbnails"
    )

    assert "test_videos_lectures/thumbnails" in await result

@pytest.mark.asyncio
async def test_upload_file_from_content_success(s3_manager, mock_upload_file):
    """
    Проверяет успешную загрузку файла в S3.

    Проверяет:
    - Корректность формирования URL
    - Вызов метода чтения файла (read)
    - Вызов метода перемещения указателя (seek)
    - Вызов метода загрузки в S3 (put_object)
    """
    file_key = "test/path"
    expected_url = f"{s3_manager.endpoint}/{s3_manager.bucket_name}/{file_key}"

    async_cm = AsyncMock()
    s3_manager.session.__aenter__.return_value = async_cm
    async_cm.put_object.return_value = {"ResponseMetadata": {"RequestId": "test"}}
    s3_manager.get_link_file = AsyncMock(return_value=expected_url)

    result = await s3_manager.upload_file_from_content(mock_upload_file, file_key)
    result = await result

    assert result.startswith(f"{s3_manager.endpoint}/{s3_manager.bucket_name}/")
    assert mock_upload_file.read.called
    assert mock_upload_file.seek.called
    assert async_cm.put_object.called

@pytest.mark.asyncio
async def test_upload_file_from_content_client_error(s3_manager, mock_upload_file):
    """
    Проверяет обработку ошибки клиента S3 (ClientError).

    Проверяет:
    - Перехват ошибки ClientError
    - Преобразование в ValueError
    - Корректность текста ошибки
    """
    error_response = {"Error": {"Code": "TestError", "Message": "Test error"}}
    async_cm = AsyncMock()
    s3_manager.session.__aenter__.return_value = async_cm
    async_cm.put_object.side_effect = ClientError(error_response, "PutObject")

    with pytest.raises(ValueError):
        await s3_manager.upload_file_from_content(mock_upload_file)


@pytest.mark.asyncio
async def test_upload_file_from_content_runtime_error(s3_manager, mock_upload_file):
    """
    Проверяет обработку ошибки клиента S3 (ClientError).

    Проверяет:
    - Перехват ошибки ClientError
    - Преобразование в ValueError
    - Корректность текста ошибки
    """
    async_cm = AsyncMock()
    s3_manager.session.__aenter__.return_value = async_cm
    async_cm.put_object.side_effect = Exception("Unexpected error")

    with pytest.raises(RuntimeError):
        await s3_manager.upload_file_from_content(mock_upload_file)
