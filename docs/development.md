### Разработка

Перед началом разработки нужно сунуть .env.dev в каждый сервис и в корень.
В дальнешем можно будет обойтись параметрами по умолчанию из настроек и избавиться от .env.dev. Может это будет удобно, разрабатывать тогда можно без .env.dev. вообще.

### Первый запуск
Клонируем и ставим зависимости для КАЖДОГО сервиса:
```bash
# Для Windows (powershell):
cd api_gateway
.\scripts\setup.bat   # создаст venv, активирует его и установит зависимости

cd ..\auth-service
.\scripts\setup.bat
```

```bash
# Для Linux:
cd api_gateway
./scripts/setup.sh   # создаст venv, активирует его и установит зависимости

cd ..\auth-service
./scripts/setup.sh
```

```bash
cd api_gateway # или находясь в api_gateway или в auth-service
                                                # не нужно выполнять эту команду
uv run infra-up   # команда сама сделает cd .. и поднимет все сервисы
```


### Более подробно

Можно через uv:

```bash
# Поднять всю инфраструктуру
uv run infra-up

# Посмотреть что поднялось:
- RabbitMQ: http://localhost:15672 (admin/admin)
- PostgreSQL: localhost:5432 (postgres/postgres) - понятно, что не в браузере
- Redis: localhost:6379 (pass: default) - понятно, что не в браузере
- API Gateway: http://localhost:8001
- Auth Service: http://localhost:8002

# Логи всех сервисов
uv run infra-logs

# Логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs api_gateway

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
docker-compose -f docker-compose.dev.yml logs api_gateway

# Перезапустить один сервис
docker-compose -f docker-compose.dev.yml restart auth_service

# Перезапустить один сервис
docker-compose -f docker-compose.dev.yml restart auth_service

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
- 8001 - API Gateway
- 8002 - Auth Service

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
- Database: testdb

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
- http://localhost:8001/docs  # API Gateway
- http://localhost:8002/docs  # Auth Service


### После исправления косяков связанных с RabbitMQ

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

### Просто после исправления косяков
```bash
uv run infra-restart
```
или
```bash
uv run infra-down
uv run infra-up
```