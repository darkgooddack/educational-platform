### Первый запуск
```bash
# Для Windows (powershell):
.\scripts\setup.ps1   # создаст venv, активирует его и установит зависимости
```

```bash
# Для Linux:
./scripts/setup.sh   # создаст venv, активирует его и установит зависимости
```


```bash
uv run dev
# или
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

# Логи конкретного контейнера
docker-compose -f docker-compose.dev.yml logs backend

# Перезапустить
uv run infra-restart

# Остановить всё
uv run infra-down

# Пересобрать контейнеры (если менял Dockerfile)
uv run infra-build
```

Или напрямую в консоли:

```bash
# Поднять контейнеры и показать логи
docker-compose -f docker-compose.dev.yml up

# Перестроить образы (когда меняешь код)
docker-compose -f docker-compose.dev.yml build

# Посмотреть логи конкретного контейнера
docker-compose -f docker-compose.dev.yml logs backend

# Перезапустить один контейнер
docker-compose -f docker-compose.dev.yml restart backend

# Перезапустить один контейнер
docker-compose -f docker-compose.dev.yml restart backend

# Выполнить команду внутри контейнера
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres

# Посмотреть статус контейнеров
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
- host: localhost
- port: 6379
- password: default

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