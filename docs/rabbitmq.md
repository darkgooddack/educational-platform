# RabbitMQ

#### Установка RabbitMQ:

Для запуска локально на Windows:
- Cсылка на официальную документацию: https://www.rabbitmq.com/docs/download
- Возможно придется установить: https://www.erlang.org/downloads

Нужно добавить путь к RabbitMQ в PATH Windows.
1. Найди где установлен RabbitMQ (обычно это):
```
C:\Program Files\RabbitMQ Server\rabbitmq_server-{version}\sbin
```
2. Добавь в PATH:
- Нажми Win + X
- Выбери "Система"
- "Дополнительные параметры системы"
- "Переменные среды"
- Найди PATH
- Добавь путь к sbin папке RabbitMQ

3. Или через PowerShell (от админа):
```
$rabbitPath = "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12.12\sbin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$rabbitPath", "Machine")
```
5. Перезапусти PowerShell и команды заработают!

#### Запуск RabbitMQ через docker (почему-то зависло, может от долгой установки):
```bash
# latest RabbitMQ 4.0.x
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```
#### RabbitMQ доступен:
- AMQP порт: localhost:5672
- Web UI: http://localhost:15672
- Логин/пароль по умолчанию: guest/guest

#### Начало работы:
```
# Открой в браузере
http://localhost:15672

# Дефолтные креды:
Username: guest
Password: guest
```

#### Команды:
```bash
# Статус сервиса
rabbitmqctl status

# Список очередей
rabbitmqctl list_queues

# Список пользователей
rabbitmqctl list_users
```