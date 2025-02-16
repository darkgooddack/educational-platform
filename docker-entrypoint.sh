#!/usr/bin/bash

echo "Создание директории для логов и файла логов"
mkdir -p /monitoring/logs
touch /monitoring/logs/app.log
chmod 666 /monitoring/logs/app.log

echo "Запуск сервиса"
uv run start