#!/usr/bin/bash
# При нынешней структуре приходится использовать директорию backend внутри контейнера, чтобы не было проблем с импортами
echo "Запуск скрипта docker-entrypoint.sh"

echo "Применение миграции"
cd /usr/src/app/backend && alembic upgrade head

echo "Запуск сервера uvicorn"
cd /usr/src/app && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*
