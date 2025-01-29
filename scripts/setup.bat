@echo off
chcp 65001 > nul

IF NOT EXIST ".venv" (
    echo 🚀 Создаю виртуальное окружение...
    uv venv
    echo ✨ Виртуальное окружение создано!

    echo 🔌 Активирую виртуальное окружение...
    call .\.venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано!

    echo 📦 Устанавливаю зависимости...
    uv pip install -e ".[dev]"
    echo 🎉 Установка завершена успешно!
) ELSE (
    echo 🔌 Активирую виртуальное окружение...
    call .\.venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано!
)
