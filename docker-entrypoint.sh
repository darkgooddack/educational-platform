#!/usr/bin/bash

set -e

echo "Создаём файл логов и выставляем права" 
touch /app.log 2>&1 || echo "Не удалось создать файл логов: $?"
chmod 666 /app.log 2>&1 || echo "Не удалось установить права: $?"


echo "Запуск сервиса"
uv run start