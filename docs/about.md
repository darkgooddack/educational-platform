# Educational Platform

Платформа для онлайн-обучения.

## Структура проекта
```
app
├── main.py
├── __init__.py
├── core
│   ├── lifespan.py
│   ├── logging.py
│   ├── security.py
│   ├── clients
│   │   ├── rabbitmq.py
│   │   ├── redis.py
│   │   └── __init__.py
│   ├── config
│   │   ├── app.py
│   │   ├── settings.py
│   │   └── __init__.py
│   ├── dependencies
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── rabbitmq.py
│   │   ├── redis.py
│   │   └── __init__.py
│   ├── exceptions
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── base.py
│   │       ├── __init__.py
│   │       └── auth
│   │           ├── auth.py
│   │           ├── oauth.py
│   │           ├── security.py
│   │           ├── users.py
│   │           └── __init__.py
│   ├── middlewares
│   │   ├── docs_auth.py
│   │   ├── logging.py
│   │   └── __init__.py
│   └── migrations
│       ├── env.py
│       ├── README
│       ├── script.py.mako
│       └── versions
│           ├── c54703e51b42_add_fields_for_oauth.py
│           └── f58b4d906a74_initial_commit.py
├── models
│   ├── __init__.py
│   └── v1
│       ├── base.py
│       ├── users.py
│       └── __init__.py
├── routes
│   ├── __init__.py
│   └── v1
│       ├── main.py
│       ├── __init__.py
│       └── auth
│           ├── auth.py
│           ├── oauth.py
│           ├── register.py
│           └── __init__.py
├── schemas
│   ├── __init__.py
│   └── v1
│       ├── base.py
│       ├── __init__.py
│       └── auth
│           ├── auth.py
│           ├── oauth.py
│           ├── register.py
│           ├── users.py
│           └── __init__.py
└── services
    ├── __init__.py
    └── v1
        ├── base.py
        ├── __init__.py
        └── auth
            ├── auth.py
            ├── oauth.py
            ├── users.py
            └── __init__.py

```

### Разработка
Для разработки используется uv package manager.


#### Первый запуск

Windows:
```bash
.\scripts\setup.ps1
```
Linux:
```bash
./scripts/setup.sh
```
#### Команды

#### Запуск для разработки
```bash
# Запуск в режиме разработки (с hot-reload), но необходима локальная rabbitmq, иначе выпадет ошибка, даже с контейнерами отдельно не заработала...
uv run dev
```
# Запуск инфраструктуры (контейнеров)
```bash
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
# Запуск только uvicorn сервера (не искользуется)
uv run serve

# Полный запуск (миграции + сервер) - используется при деплое в docker-entrypoint.sh
uv run start
```

### Требования
- Python 3.11+
- Docker
- uv package manager