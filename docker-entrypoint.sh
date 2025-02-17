#!/usr/bin/bash

set -e

echo "Создаём директорию для логов"
mkdir -p /monitoring/logs 2>&1 || echo "Не удалось создать директорию: $?"
ls -la /monitoring/logs 2>&1 || echo "Не удалось получить список файлов: $?"

echo "Создаём файл логов и выставляем права" 
touch /monitoring/logs/app.log 2>&1 || echo "Не удалось создать файл логов: $?"
chmod 666 /monitoring/logs/app.log 2>&1 || echo "Не удалось установить права: $?"


echo "Запуск сервиса"
uv run start