"""
Модуль менеджера данных для работы с S3.
Этот модуль предоставляет класс S3DataManager, который используется для управления данными в S3.
Он содержит методы для создания бакета, проверки существования бакета, загрузки файлов и другие операции.
"""
import logging
import os
import uuid
from typing import List
import aiofiles
from fastapi import UploadFile

from botocore.exceptions import ClientError
from app.core.config import config
from app.core.dependencies.s3 import S3Session


class SessionMixin:
    """
    Смешанный класс для работы с сессией S3.
    Содержит (может содержать) общие методы для работы с сессией S3.
    """

    def __init__(self, session: S3Session):
        self.session = session

class S3DataManager(SessionMixin):
    """
    Класс менеджера данных для работы с S3.

    Methods:
        create_bucket: Создает бакет в S3.
        bucket_exists: Проверяет существование бакета.
        upload_file_from_path: Загружает файл-подобный объект в S3 из файловой системы.
        upload_file_from_content: Загружает файл-подобный объект в S3 из байтового представления.
        upload_multiple_files_from_path: Загружает несколько файлов-подобных объектов в S3 из файловой системы.
        upload_multiple_files_from_content: Загружает несколько файлов-подобных объектов в S3 из байтового представления.
        get_link_file: Получает ссылку на файл в S3.
        download_file: Скачивает файл из S3.
        download_multiple_files: Скачивает несколько файлов из S3.
        get_file_keys: Получает список ключей файлов в бакете.
        download_all_files: Скачивает все файлы из S3.
        delete_file: Удаляет файл из S3.

    """

    def __init__(self, session: S3Session | None):
        if session is None:
            self.endpoint = None
            self.bucket_name = None
            return
        super().__init__(session)
        self.endpoint = config.aws_endpoint
        self.bucket_name = config.aws_bucket_name
        self.logger = logging.getLogger("S3DataManagerLogger")

    async def create_bucket(self, bucket_name: str = None) -> None:
        """
        Создание бакета в S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)

        Returns: None
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            async with self.session as s3:
                await s3.create_bucket(Bucket=bucket_name)
        except ClientError as e:
            raise ValueError(f"Ошибка при создании бакета: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при создании бакета: {e}") from e

    async def bucket_exists(self, bucket_name: str = None) -> bool:
        """
        Проверка существования бакета.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)

        Returns: bool
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            async with self.session as s3:
                await s3.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
        raise ValueError(f"Ошибка при проверке наличия бакета: {e}") from e

    async def file_exists(self, file_key: str, bucket_name: str = None) -> bool:
        """
        Проверка существования файла в S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_key: str - ключ файла в S3

        Returns: bool
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            async with self.session as s3:
                await s3.head_object(Bucket=bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
        raise ValueError(f"Ошибка при проверке наличия файла: {e}") from e

    async def upload_file_from_path(
        self, file_path: str, file_key: str, bucket_name: str = None
    ) -> None:
        """
        Загрузка файл-подобного объекта в S3 из файловой системы.
        Файл должен быть открыт в бинарном режиме.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_path: str - путь к файлу для загрузки
            file_key: str - ключ файла в S3

        Returns: None
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")
        try:
            async with aiofiles.open(file=file_path, mode="rb") as file:
                async with self.session as s3:
                    await s3.upload_fileobj(
                        Fileobj=file,
                        Bucket=bucket_name,
                        Key=file_key,
                    )
                return self.get_link_file(file_key, bucket_name)
        except ClientError as e:
            raise ValueError(f"Ошибка при загрузке файла: {e}") from e
        except IOError as e:
            raise ValueError(f"Ошибка при открытии файла: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке файла: {e}") from e

    async def upload_file_from_content(
        self, file: UploadFile, file_key: str = "", bucket_name: str = None
    ) -> None:
        """
        Прямая загрузка файл-подобного объекта в S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file: UploadFile - файл-подобный объект для загрузки
            file_key: str - ключ файла в S3 (путь в бакете)

        Returns:
            str: URL загруженного файла в S3
        """
        if bucket_name is None:
            bucket_name = self.bucket_name
        self.logger.info("=== Начало загрузки файла ===")
        self.logger.info("Параметры авторизации:")
        self.logger.info(f"Access Key ID: {self.session.access_key_id[:4]}***") 
        self.logger.info(f"Secret Key: {self.session.secret_access_key[:4]}***")
        self.logger.info(f"Регион: {self.session.region_name}")
        self.logger.info(f"Endpoint: {self.endpoint}")

        self.logger.info("Параметры файла:")
        self.logger.info(f"Имя файла: {file.filename}")
        self.logger.info(f"Content-Type: {file.content_type}") 
        self.logger.info(f"Размер: {len(await file.read())} байт")
        self.logger.info(f"Bucket: {bucket_name}")
        self.logger.info(f"Key: {file_key}")
        self.logger.debug(
            "Загрузка файла: name=%s, type=%s, size=%d, bucket=%s, key=%s",
            file.filename,
            file.content_type,
            len(await file.read()),  # прочитаем размер
            bucket_name,
            file_key
        )
        await file.seek(0)  # вернем указатель в начало
        try:
            file_content = await file.read()
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_key = (
                f"{file_key}/{unique_filename}" if file_key else f"{unique_filename}"
            )
            self.logger.debug("Вызов put_object с параметрами: bucket=%s, key=%s", bucket_name, file_key)

            async with self.session as s3:
                response = await s3.put_object(
                    Bucket=bucket_name,
                    Key=file_key,
                    Body=file_content,
                    ContentType=file.content_type,
                    ACL='public-read',
                    CacheControl='max-age=31536000',
                )
                self.logger.info("Ответ от S3:")    
                self.logger.info(f"Status: {response['ResponseMetadata']['HTTPStatusCode']}")
                self.logger.info(f"RequestId: {response['ResponseMetadata']['RequestId']}")
                self.logger.info("=== Загрузка успешно завершена ===")
            return self.get_link_file(file_key, bucket_name)
        except ClientError as e:
            self.logger.error("=== Ошибка загрузки файла ===")
            self.logger.error(f"Код ошибки: {e.response['Error']['Code']}")
            self.logger.error(f"Сообщение: {e.response['Error']['Message']}")
            self.logger.error(f"RequestId: {e.response['ResponseMetadata']['RequestId']}")
            self.logger.error(f"HTTP Status: {e.response['ResponseMetadata']['HTTPStatusCode']}")
            raise ValueError(f"Ошибка при загрузке файла: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке файла: {e}") from e

    async def upload_multiple_files_from_path(
        self,
        file_paths: List[str],
        file_keys: List[str],
        bucket_name: str = None,
    ) -> List[str]:
        """
        Загрузка нескольких файлов в S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_paths: List[str] - список путей к файлам для загрузки
            file_keys: List[str] - список ключей файлов в S3

        Returns:
            List[str] - список ключей загруженных файлов
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        uploaded_files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл {file_path} не найден")
        try:
            for file_path, file_key in zip(file_paths, file_keys):
                await self.upload_file_from_path(file_path, file_key, bucket_name)
                uploaded_files.append(file_key)
            return uploaded_files
        except ClientError as e:
            raise ValueError(f"Ошибка при загрузке файлов: {e}") from e
        except IOError as e:
            raise ValueError(f"Ошибка при открытии файлов: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке файлов: {e}") from e

    async def upload_multiple_files_from_content(
        self,
        files: List[UploadFile],
        file_keys: List[str],
        bucket_name: str = None,
    ) -> List[str]:
        """
        Загрузка нескольких файлов в S3 напрямую из контента.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            files: List[UploadFile] - список файлов для загрузки
            file_keys: List[str] - список ключей файлов в S3

        Returns:
            List[str] - список ключей загруженных файлов
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        uploaded_files = []
        try:
            for file, file_key in zip(files, file_keys):
                await self.upload_file_from_content(file, file_key, bucket_name)
                uploaded_files.append(file_key)
            return uploaded_files
        except ClientError as e:
            raise ValueError(f"Ошибка при загрузке файлов: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке файлов: {e}") from e

    async def get_link_file(self, file_key: str, bucket_name: str = None) -> str:
        """
        Получение ссылки на файл в S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_key: str - ключ файла в S3

        Returns:
            str - ссылка на файл в S3 в виде строки: {endpoint}/{bucket_name}/{file_key}
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            return f"{self.endpoint}/{bucket_name}/{file_key}"
        except ClientError as e:
            raise ValueError(f"Ошибка при получении ссылки на файл: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении ссылки на файл: {e}") from e

    async def download_file(
        self, file_key: str, file_path: str, bucket_name: str = None
    ) -> None:
        """
        Скачивание файл-подобного объекта из S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_key: str - ключ файла в S3
            file_path: str - путь к файлу для скачивания

        Returns: None
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            async with aiofiles.open(file=file_path, mode="wb") as file:
                async with self.session as s3:
                    await s3.download_fileobj(
                        Bucket=bucket_name,
                        Key=file_key,
                        Fileobj=file
                    )
        except ClientError as e:
            raise ValueError(f"Ошибка при скачивании файла: {e}") from e
        except IOError as e:
            raise ValueError(f"Ошибка при открытии файла для записи: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при скачивании файла: {e}") from e

    async def download_multiple_files(
        self, file_keys: List[str], file_paths: List[str], bucket_name: str = None
    ) -> List[str]:
        """
        Скачивание нескольких файлов из S3.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_keys: List[str] - список ключей файлов в S3
            file_paths: List[str] - список путей к файлам для скачивания

        Returns:
            List[str] - список ключей скаченных файлов
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        downloaded_files = []
        try:
            for file_key, file_path in zip(file_keys, file_paths):
                await self.download_file(file_key, file_path, bucket_name)
                downloaded_files.append(file_key)
            return downloaded_files
        except ClientError as e:
            raise ValueError(f"Ошибка при скачивании файлов: {e}") from e
        except IOError as e:
            raise ValueError(f"Ошибка при открытии файлов для записи: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при скачивании файлов: {e}") from e

    async def get_file_keys(
        self, prefix: str = "", bucket_name: str = None
    ) -> List[str]:
        """
        Получение списка файлов в бакете.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            prefix: str - префикс для фильтрации файлов (по умолчанию пустой)

        Returns:
            List[str] - список ключей файлов в S3
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            async with self.session as s3:
                response = await s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix
                )
            keys = []
            for obj in response.get("Contents", []):
                keys.append(obj["Key"])
            return keys
        except ClientError as e:
            raise ValueError(f"Ошибка при получении списка файлов: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении списка файлов: {e}") from e

    async def download_all_files(
        self, folder_path: str, prefix: str = "", bucket_name: str = None
    ) -> None:
        """
        Скачивание всех файлов из бакета.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            folder_path: str - путь к папке для скачивания файлов
            prefix: str - префикс для фильтрации файлов (по умолчанию пустой)

        Returns: None
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        downloaded_files = []
        try:
            file_keys = await self.get_file_keys(prefix, bucket_name)
            file_paths = [os.path.join(folder_path, file_key) for file_key in file_keys]
            downloaded_files = await self.download_multiple_files(
                file_keys, file_paths, bucket_name
            )
            return downloaded_files
        except ClientError as e:
            raise ValueError(f"Ошибка при скачивании файлов: {e}") from e
        except IOError as e:
            raise ValueError(f"Ошибка при открытии файлов для записи: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при скачивании файлов: {e}") from e

    async def delete_file(self, file_key: str, bucket_name: str = None) -> bool:
        """
        Удаление файла из бакета.

        Args:
            bucket_name: str - имя бакета для создания (по умолчанию из конфигурации)
            file_key: str - ключ файла для удаления

        Returns: None
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            async with self.session as s3:
                await s3.delete_object(Bucket=bucket_name, Key=file_key)
            return True
        except ClientError as e:
            raise ValueError(f"Ошибка при удалении файла из бакета: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ошибка при удалении файла из бакета: {e}") from e
