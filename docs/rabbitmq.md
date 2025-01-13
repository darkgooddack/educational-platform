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

#### Запуск RabbitMQ через docker:
```bash
# latest RabbitMQ 4.0.x
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management

#или

docker run -d --hostname rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
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

### Если не работает:

Например ошибка такая:
```
Error: unable to perform an operation on node 'rabbit@DESKTOP-FL1E7S4'.

# Бла-бла-бла

 * TCP connection succeeded but Erlang distribution failed
```
Останови все процессы RabbitMQ:
```bash
net stop RabbitMQ
```

Удали старый cookie файл:
```bash
del "%USERPROFILE%\.erlang.cookie"
```

Переустанови RabbitMQ полностью:
```bash
choco uninstall rabbitmq
choco install rabbitmq
```

Запусти службу:
```bash
net start RabbitMQ
```


Проверь статус:
```bash
rabbitmqctl status
```

### Или вообще все плохо:

1. Открой диспетчер задач (Ctrl+Shift+Esc)
2. Найди все процессы связанные с RabbitMQ и убей их нахрен
3. Удали RabbitMQ полностью через PowerShell:
```bash
choco uninstall rabbitmq erlang --force
```
1. Установи RabbitMQ через Chocolatey:
```bash
choco install erlang
choco install rabbitmq
```
1. Запусти RabbitMQ:
```bash
net start RabbitMQ
```

Но лучше все делать через docker и не засирать систему.