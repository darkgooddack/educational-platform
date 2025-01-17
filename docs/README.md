# Educational Platform

Платформа для онлайн-обучения с микросервисной архитектурой.

## Структура проекта
```
educational-platform/
├── api-gateway/ # API Gateway сервис
├── auth-service/ # Сервис авторизации
├── course-service/ # Сервис курсов - для примера
└── user-service/ # Сервис пользователей - для примера
```


## Порядок запуска (Лучше сразу перейти к Разработка, пока что)

### 1. Запуск инфраструктуры
> [!CAUTION]
> PostgreSQL и Redis поднимаются отдельно через Dokploy
```bash
# Запуск PostgreSQL -
docker compose up postgres -d

# Запуск Redis
docker compose up redis -d

# Запуск RabbitMQ
docker compose up rabbitmq -d

```

### 2. Запуск сервисов
```bash
# Запуск API Gateway
docker compose up api-gateway -d

# Запуск сервисов авторизации, курсов и пользователей (для примера)
docker compose up auth-service course-service user-service -d
```

Или по отдельности для разработки:

```bash
# Сервис авторизации (порт 8000)
cd api-gateway
uv pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

```bash
# Сервис авторизации (порт 8001)
cd auth-service
uv pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

```bash
# Сервис пользователей (порт 8002)
cd user_service
uv pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8002
```

```bash
# Сервис курсов (порт 8003)
cd course_service
uv pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8003
```
### 3. Запуск тестов
> [!CAUTION]
> Тесты пока отсутствуют
```bash
# Запуск тестов

docker compose up test
```

### Проверка работоспособности
API документация доступна по адресам:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Разработка
Для разработки используется uv package manager.


#### Первый запуск

Windows:
```bash
cd api-gateway  # или cd auth-service, cd course-service, cd user-service
.\scripts\setup.bat
uv run dev
```
Linux:
```bash
cd api-gateway # или cd auth-service, cd course-service, cd user-service
./scripts/setup.sh
uv run dev
```
#### Команды

#### Запуск для разработки
```bash
# Запуск в режиме разработки (с hot-reload), но необходима локальная rabbitmq
uv run dev
```
# Запуск инфраструктуры
```bash
cd ./api-gateway
uv run infra-up
```

#### Работа с миграциями
```bash
# Применить все миграции
uv run migrate

# Создать новую миграцию
uv run create_migration "название_миграции"

# Откатить последнюю миграцию
uv run rollback
```

#### Линтинг и форматирование
```bash
# Запуск всех линтеров (black + isort + flake8 + mypy)
uv run lint

# Только форматирование кода (black + isort)
uv run format

# Проверка типов и стиля (flake8 + mypy)
uv run check
```

#### Тестирование
```bash
# Запуск тестов
uv run test
```

#### Запуск сервера
```bash
# Запуск только uvicorn сервера
uv run serve

# Полный запуск (миграции + сервер) - используется в docker-entrypoint.sh
uv run start
```

### Требования
- Python 3.11+
- Docker
- uv package manager