#!/usr/bin/bash

set -e

echo "Создаём файл логов и выставляем права" 
touch /var/log/app.log 2>&1 || echo "Не удалось создать файл логов: $?"
chmod 666 /var/log/app.log 2>&1 || echo "Не удалось установить права: $?"


echo "Запуск сервиса"
uv run start