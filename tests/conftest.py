import sys
import os
from pathlib import Path
import pytest
from aio_pika import Channel
from unittest.mock import AsyncMock

@pytest.fixture
def channel():
    return AsyncMock(spec=Channel)

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))