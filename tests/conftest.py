import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from fastapi import UploadFile
from app.core.dependencies.s3 import S3Session
from app.core.storages.s3.base import S3DataManager


@pytest.fixture
def s3_session():
    session = AsyncMock()
    session.put_object = AsyncMock()
    return session

@pytest.fixture
def s3_manager(s3_session):
    manager = S3DataManager(S3Session())
    manager.session = s3_session
    manager.endpoint = "https://s3.storage.selcloud.ru"
    manager.bucket_name = "education-platform"
    return manager

@pytest.fixture
def mock_upload_file():
    file = AsyncMock(spec=UploadFile)
    file.filename = "test.txt"
    file.content_type = "text/plain"
    file.read = AsyncMock(return_value=b"test content")
    file.seek = AsyncMock()
    return file

@pytest.fixture
def mock_upload_image_file(request):
    file_path = Path(__file__).parent / "fixtures" / "files" / "thumbnail.jpg"

    async def mock_read():
        with open(file_path, "rb") as f:
            return f.read()

    file = AsyncMock(spec=UploadFile)
    file.filename = file_path.name
    file.content_type = "image/jpeg"
    file.read = AsyncMock(side_effect=mock_read)
    file.seek = AsyncMock()
    return file

@pytest.fixture
def mock_upload_video_file(request):
    file_path = Path(__file__).parent / "fixtures" / "files" / "lecture.mp4"

    async def mock_read():
        with open(file_path, "rb") as f:
            return f.read()

    file = AsyncMock(spec=UploadFile)
    file.filename = file_path.name
    file.content_type = "video/mp4"
    file.read = AsyncMock(side_effect=mock_read)
    file.seek = AsyncMock()
    return file

def pytest_configure(config):
    """Установка переменной окружения для тестов"""
    root_dir = Path(__file__).parent.parent
    os.environ["ENV_FILE"] = str(root_dir / ".env.test")

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))