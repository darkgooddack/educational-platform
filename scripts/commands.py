import os
import subprocess
from pathlib import Path
from typing import Optional
import time
import socket
import uvicorn

ENV_FILE=".env.dev"
# Получаем путь к корню проекта
ROOT_DIR = Path(__file__).parents[1]
COMPOSE_FILE_FULL = "docker-compose.dev.full.yml"
COMPOSE_FILE_WITHOUT_BACKEND = "docker-compose.dev.yml"

DEFAULT_PORTS = {
    'FASTAPI': 8000,
    'RABBITMQ': 5672,      # Порт для AMQP
    'RABBITMQ_UI': 15672,  # Порт для веб-интерфейса
    'POSTGRES': 5432,
    'REDIS': 6379,
    'PGADMIN': 5050,
    'REDIS_COMMANDER': 8081,
    'GRAFANA': 3334,
    'LOKI': 3100
}

def run_compose_command(command: str | list, compose_file: str = COMPOSE_FILE_FULL, env: dict = None) -> None:
    """Запускает docker-compose команду в корне проекта"""
    if isinstance(command, str):
        command = command.split()

    # Обновляем переменные окружения
    environment = os.environ.copy()
    # Добавляем переменные из ENV_FILE по умолчанию
    env_file = os.path.join(ROOT_DIR, ENV_FILE)
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    environment[key] = value
    if env:
        environment.update(env)

    subprocess.run(
        ["docker-compose", "-f", compose_file] + command,
        cwd=ROOT_DIR,
        check=True,
        env=environment
    )

def infra_up():
    """Поднимаем всю инфраструктуру"""
    run_compose_command(["up", "-d"])

def infra_down():
    """Останавливаем инфраструктуру"""
    run_compose_command("down")

def infra_build():
    """Пересобираем контейнеры"""
    run_compose_command("build")

def infra_logs():
    """Смотрим логи"""
    run_compose_command("logs -f")

def infra_restart():
    """Перезапускаем сервисы"""
    run_compose_command("restart")

def infra_nuke():
    """Сносим нахрен всё и поднимаем заново"""
    # Убиваем все контейнеры
    run_compose_command(["down", "--volumes", "--remove-orphans", "--rmi", "all"])

    # Чистим все неиспользуемые volumes
    subprocess.run(["docker", "volume", "prune", "-f"], check=True)

    # Чистим все неиспользуемые images
    subprocess.run(["docker", "image", "prune", "-af"], check=True)

    # Собираем заново
    run_compose_command("build --no-cache")

    # Поднимаем
    run_compose_command(["up", "-d"])

def grafana_restart():
    """Перезапуск Grafana и связанных сервисов"""
    run_compose_command(["restart", "grafana", "loki", "promtail"], COMPOSE_FILE_WITHOUT_BACKEND)

def grafana_logs():
    """Просмотр логов Grafana и связанных сервисов"""
    run_compose_command(["logs", "-f", "grafana", "loki", "promtail"], COMPOSE_FILE_WITHOUT_BACKEND)

def grafana_rebuild():
    """Пересборка Grafana и связанных сервисов"""
    run_compose_command(["up", "-d", "--build", "grafana", "loki", "promtail"], COMPOSE_FILE_WITHOUT_BACKEND)

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

def get_available_port(default_port: int) -> int:
    port = default_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"Не могу найти свободный порт после {default_port}")

def get_port(service: str) -> int:
    """Получает порт из переменных окружения или использует значение по умолчанию"""
    service_upper = service.upper().replace('_PORT', '')
    return int(os.getenv(service, DEFAULT_PORTS[service_upper]))

def check_service(name: str, port: int, retries: int = 5, delay: int = 2) -> bool:
    """Базовая функция проверки сервиса"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(retries):
        try:
            sock.connect(('localhost', port))
            sock.close()
            return True
        except:
            print(f"⏳ Ждём {name} на порту {port}...")
            time.sleep(delay)
    return False

def check_services():
    """Проверяет доступность всех сервисов"""
    services_config = {
        'Redis': ('REDIS_PORT', 5),
        'RabbitMQ': ('RABBITMQ_UI_PORT', 5),
        'PostgreSQL': ('POSTGRES_PORT', 30),
        'Grafana': ('GRAFANA_PORT', 5),
        'Loki': ('LOKI_PORT', 5)
    }

    for service_name, (port_key, retries) in services_config.items():
        port = get_port(port_key)
        if not check_service(service_name, port, retries):
            print(f"❌ {service_name} не доступен на порту {port}!")
            return False
    return True

def start_infrastructure():
    print("🚀 Запускаем инфраструктуру...")
    try:

        # Сначала убиваем все контейнеры
        run_compose_command("down --remove-orphans")

        # Очищаем тома
        subprocess.run(["docker", "volume", "prune", "-f"], check=True)

        # Получаем свободные порты
        ports = {
            service: get_available_port(default_port)
            for service, default_port in DEFAULT_PORTS.items()
        }

        # Используем порты в docker-compose через переменные окружения
        env = {
            f"{service}_PORT": str(port)
            for service, port in ports.items()
        }

        run_compose_command(["up", "-d"], COMPOSE_FILE_WITHOUT_BACKEND, env=env)

        # Ждем доступности сервисов
        check_services()

        # Запускаем миграции после успешного поднятия PostgreSQL
        print("📦 Запускаем миграции...")
        migrate()
        print("✅ Миграции выполнены!")


        print("\n🔗 Доступные адреса:")
        print(f"📊 FastAPI Swagger:    http://localhost:{ports['FASTAPI']}/docs")
        print(f"🐰 RabbitMQ UI:       http://localhost:{ports['RABBITMQ_UI']}")
        print(f"🗄️ PostgreSQL:        localhost:{ports['POSTGRES']}")
        print(f"📦 Redis:             localhost:{ports['REDIS']}")
        print(f"🔍 PgAdmin:           http://localhost:{ports['PGADMIN']}")
        print(f"📊 Redis Commander:    http://localhost:{ports['REDIS_COMMANDER']}")
        print(f"📊 Grafana:           http://localhost:{ports['GRAFANA']}")
        print(f"📈 Loki:              http://localhost:{ports['LOKI']}\n")

        print("✅ Инфраструктура готова!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при запуске инфраструктуры: {e}")
        return False

def dev(port: Optional[int] = None):
    """
    Запуск в режиме разработки

    Args:
        port: Конкретный порт для запуска. Если None - найдет свободный
    """
    # if not check_rabbitmq():
    #     print("🔴 RabbitMQ не доступен! Запусти его командой:")
    #     print("net start RabbitMQ")
    #     return

    # print("🟢 RabbitMQ работает!")

    # Запускаем инфраструктуру
    if not start_infrastructure():
        return

    if port is None:
        port = find_free_port()


    print(f"🚀 Запускаем сервер на порту {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="debug",
        access_log=False
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
    subprocess.run(["alembic", "downgrade", "-1"], check=True)

def create_migration(name: str):
    """
    Создание новой миграции.
    """
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", name], check=True)

def echo(message: str):
    """
    Вывод сообщения (тест команды).
    """
    import sys
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        echo(message)
    subprocess.run(["echo", message], check=True)

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
    mypy_success = True
    flake8_success = True

    # Проверка mypy
    try:
        mypy_result = subprocess.run(
            ["mypy", "app/"],
            capture_output=True,
            text=True,
            check=True
        )
        mypy_errors = mypy_result.stdout.split('\n')

        mypy_error_groups = {
            'error: Incompatible': 'Несовместимые типы',
            'error: Name': 'Ошибки именования',
            'error: Missing': 'Отсутствующие типы',
            'error: Argument': 'Ошибки аргументов',
            'error: Return': 'Ошибки возвращаемых значений'
        }

        # Сначала собираем все ошибки в известные группы
        grouped_errors = set()
        for pattern, desc in mypy_error_groups.items():
            matches = [e for e in mypy_errors if pattern in e]
            if matches:
                print(f"\n🔍 MyPy - {desc}:")
                for error in matches:
                    print(f"- {error}")
                    grouped_errors.add(error)

        # Оставшиеся ошибки выводим как "Прочие"
        other_errors = [e for e in mypy_errors if e and e not in grouped_errors]
        if other_errors:
            print("\n🔍 MyPy - Прочие ошибки:")
            for error in other_errors:
                print(f"- {error}")
    except subprocess.CalledProcessError as e:
        print("❌ Найдены ошибки mypy:")
        print(e.stdout)
        mypy_success = False

    # Проверка flake8
    try:
        result = subprocess.run(
            ["flake8", "app/"],
            capture_output=True,
            text=True,
            check=True
        )
        flake8_errors = result.stdout.split('\n')

        # Группируем ошибки по типу
        error_groups = {
            'E501': 'Длинные строки',
            'F821': 'Неопределенные переменные',
            'F841': 'Неиспользуемые переменные',
            'W605': 'Некорректные escape-последовательности',
            'E262': 'Неправильные комментарии'
        }

        # Собираем известные ошибки
        grouped_errors = set()
        for code, desc in error_groups.items():
            matches = [e for e in flake8_errors if code in e]
            if matches:
                print(f"\n🔍 Flake8 - {desc}:")
                for error in matches:
                    print(f"- {error.split(':')[0]}")
                    grouped_errors.add(error)

        # Выводим оставшиеся ошибки
        other_errors = [e for e in flake8_errors if e and e not in grouped_errors]
        if other_errors:
            print("\n🔍 Flake8 - Прочие ошибки:")
            for error in other_errors:
                print(f"- {error.split(':')[0]}")

    except subprocess.CalledProcessError as e:
        print("❌ Найдены ошибки flake8: ")
        print(e.stdout)
        flake8_success = False

    return mypy_success and flake8_success

def lint():
    """
    Запуск линтера.
    """
    format()
    check()

def test():
    """
    Запуск тестов.
    """
    env = os.environ.copy()
    env["ENV_FILE"] = ".env.test"
    try:
        subprocess.run(
            ["pytest", "tests/", "-v"],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError:
        pass

def start_all():
    """Запускает миграции и сервер"""
    migrate()
    serve()
