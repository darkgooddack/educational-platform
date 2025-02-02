import pytest
from fastapi import UploadFile
from app.core.dependencies.s3 import S3Session, SessionContextManager
from app.core.storages.s3.base import S3DataManager

@pytest.fixture
def s3_manager():
    manager = S3DataManager(SessionContextManager())
    manager.endpoint = "https://s3.storage.selcloud.ru"
    manager.bucket_name = "education-platform"
    return manager

@pytest.fixture
def test_video_file():
    file_path = "tests/fixtures/files/lecture.mp4"
    file = UploadFile(
        file=open(file_path, "rb"),
        filename="test_lecture.mp4",
        headers={"content-type": "video/mp4"}
    )
    return file

@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_video_upload(s3_manager, test_video_file):
    result = await s3_manager.upload_file_from_content(
        test_video_file,
        "integration_test/videos"
    )
    assert result.startswith(f"{s3_manager.endpoint}/{s3_manager.bucket_name}/")
