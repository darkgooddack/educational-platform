### Особенности разработки

- venv - устанавливается там, где находится pyproject.toml файл (в корне каждого микросервиса), это банально, но хочется все делать из корня репозитория...
- в каждом микросервисе есть скрипт setup.sh (setup.ps1), который создаёт venv, активирует его и устанавливает зависимости вместе с dev.
- инфраструктура на контейнерах локально поднимается из любого микросервиса (команда uv run infra-up, которая запускает docker-compose.dev.yml), неважно из какого, всё равно поднимается одинаково всё.
- можно установить rabbitmq локально, а базу данных через sqlite, тогда пользоваться командой uv run dev (но нужно все настроить)
- весь deploy производится на сервер (с dokploy) через репозиторий (пока без тестов) и поднимается по средствам docker-compose.yml

### Первый запуск
Клонируем и ставим зависимости для КАЖДОГО сервиса:
```bash
# Для Windows (powershell):
.\scripts\setup.ps1   # создаст venv, активирует его и установит зависимости
```

```bash
# Для Linux:
./scripts/setup.sh   # создаст venv, активирует его и установит зависимости
```

> [!CAUTION]
> Работает нормально пока только этот вариант, uv run dev пока не поднимается
```bash
uv run infra-up
```


### Более подробно по локальной инфраструктуре
> [!CAUTION]
> Все наименования контейнеров другие, не как в примерах команд.

Можно через uv:

```bash
# Поднять всю инфраструктуру
uv run infra-up

# Посмотреть что поднялось:
- 🐰 RabbitMQ UI: http://localhost:15672 (admin/admin) или (quest/quest)
- 🗄️ PostgreSQL: localhost:5432 (postgres/postgres) - понятно, что не в браузере
- 📦 Redis: localhost:6379 (pass: default) - понятно, что не в браузере
- 📊 FastAPI Swagger:: http://localhost:8000

# Логи всех сервисов
uv run infra-logs

# Логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs backend

# Перезапустить сервис
uv run infra-restart

# Остановить всё
uv run infra-down

# Пересобрать контейнеры (если менял Dockerfile)
uv run infra-build
```

Или напрямую в консоли:

```bash
# Поднять сервисы и показать логи
docker-compose -f docker-compose.dev.yml up

# Перестроить образы (когда меняешь код)
docker-compose -f docker-compose.dev.yml build

# Посмотреть логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs backend

# Перезапустить один сервис
docker-compose -f docker-compose.dev.yml restart backend

# Перезапустить один сервис
docker-compose -f docker-compose.dev.yml restart backend

# Выполнить команду внутри контейнера
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres

# Посмотреть статус сервисов
docker-compose -f docker-compose.dev.yml ps

# Через psql
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres testdb
```

### Порты смотрят в наружу:
- 15672 - RabbitMQ админка
- 5432 - PostgreSQL
- 6379 - Redis
- 8000 - Swagger UI

### Подключения для отладки

#### База данных
```bash
# Через psql
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres testdb
```

#### Через любой GUI-клиент (DBeaver, pgAdmin):
- Host: localhost
- Port: 5432
- User: postgres
- Password: postgres
- Database: educational_db

#### Redis
```bash
# Через redis-cli
docker-compose -f docker-compose.dev.yml exec redis redis-cli -a default
```

#### Или через RedisInsight:
- ost: localhost
- ort: 6379
- assword: default

#### Веб-интерфейс
- http://localhost:15672
- login: admin
- password: admin

#### Swagger UI
- http://localhost:8000/docs  # API


### Рекомендации
#### После исправления косяков связанных с RabbitMQ

Нужно удалить существующую очередь в RabbitMQ и пересоздать её с правильными параметрами:
```bash
# Останавливаем все
uv run infra-down

# Чистим все контейнеры и тома
docker system prune -a --volumes

# Поднимаем заново
uv run infra-up
```
Это пересоздаст RabbitMQ с чистой базой

#### Просто после исправления косяков
```bash
uv run infra-restart
```
или
```bash
uv run infra-down
docker system prune -f
uv run infra-up
```