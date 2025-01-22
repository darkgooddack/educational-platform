# Educational Platform

Платформа для онлайн-обучения.

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
# Запуск в режиме разработки (с hot-reload)
uv run dev
```
# Запуск инфраструктуры (все в контейнерах)
```bash
uv run infra-up
```

#### Работа с миграциями
```bash
# Применить все миграции
uv run migrate

# Создать новую миграцию (пока не работает)
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