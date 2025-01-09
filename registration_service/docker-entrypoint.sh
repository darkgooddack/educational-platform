#!/usr/bin/bash
echo "Запуск скрипта docker-entrypoint.sh"

echo "Применение миграции для сервиса регистрации"
uv run alembic upgrade head

echo "Запуск сервера uvicorn сервиса регистрации"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*