import subprocess
import uvicorn
import time
import socket
from typing import Optional

def find_free_port(start_port: int = 8000) -> int:
    """Ищет свободный порт, начиная с указанного"""
    port = start_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("Нет свободных портов! Ахуеть!")

def check_rabbitmq():
    """Проверяет доступность RabbitMQ"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for _ in range(5):  # 5 попыток
        try:
            sock.connect(('localhost', 5672))
            sock.close()
            return True
        except:
            print("Ждём RabbitMQ...")
            subprocess.run(["net", "start", "RabbitMQ"])
            time.sleep(2)
    return False

def dev(port: Optional[int] = None):
    """
    Запуск в режиме разработки

    Args:
        port: Конкретный порт для запуска. Если None - найдет свободный
    """
    if not check_rabbitmq():
        print("🔴 RabbitMQ не доступен! Запусти его командой:")
        print("net start RabbitMQ")
        return

    print("🟢 RabbitMQ работает!")
    if port is None:
        port = find_free_port()

    print(f"🚀 Запускаем сервер на порту {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

def serve(port: Optional[int] = None):
    """
    Запускает uvicorn сервер

    Args:
        port: Конкретный порт для запуска. Если None - найдет свободный
    """
    if port is None:
        port = find_free_port()

    print(f"🚀 Запускаем сервер на порту {port}")
    subprocess.run([
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--proxy-headers",
        "--forwarded-allow-ips=*"
    ], check=True)

def migrate():
    """
    Запуск миграций.
    """
    subprocess.run(["alembic", "upgrade", "head"], check=True)

def rollback():
    """
    Откат миграций.
    """
    subprocess.run(["alembic", "downgrade", "head"], check=True)

def create_migration(name: str):
    """
    Создание новой миграции.
    """
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", name], check=True)

def lint():
    """
    Запуск линтера.
    """
    subprocess.run(["black", "app/"], check=True)
    subprocess.run(["isort", "app/"], check=True)
    subprocess.run(["flake8", "app/"], check=True)
    subprocess.run(["mypy", "app/"], check=True)

def format():
    """
    Форматирование кода.
    """
    subprocess.run(["black", "app/"], check=True)
    subprocess.run(["isort", "app/"], check=True)

def check():
    """
    Проверка кода.
    """
    subprocess.run(["flake8", "app/"], check=True)
    subprocess.run(["mypy", "app/"], check=True)

def test():
    """
    Запуск тестов.
    """
    subprocess.run(["pytest", "tests/", "-v"], check=True)

def start_all():
    """Запускает миграции и сервер"""
    migrate()
    serve()