# Educational Platform

Платформа для онлайн-обучения с микросервисной архитектурой.

## Структура проекта
```
educational-platform/
├── api-gateway/ # API Gateway сервис
└── auth-service/ # Сервис авторизации
...
```

### Разработка
Для разработки используется uv package manager.


#### Первый запуск

Windows:
```bash
cd api-gateway  # или cd auth-service
.\scripts\setup.ps1
```
Linux:
```bash
cd api-gateway # или cd auth-service
./scripts/setup.sh
```
#### Команды

#### Запуск для разработки (индивидуально для каждого сервиса)
```bash
# Запуск в режиме разработки (с hot-reload), но необходима локальная rabbitmq, иначе выпадет ошибка
uv run dev
```
# Запуск инфраструктуры (контейнеров)
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
# Запуск тестов (пока не работает, тестов нет :( )
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