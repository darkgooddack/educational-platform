План:

Почтовый сервис:
```python
from email.mime.text import MIMEText
import smtplib
from typing import List

from app.core.config import config

class EmailService:
    def __init__(self):
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.sender_email = config.sender_email
        self.password = config.smtp_password.get_secret_value()

    async def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = to_email

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.password)
            server.send_message(msg)
```

RabbitMQ producer для отправки задач

```python
import json
from aio_pika import Message, connect_robust
from app.core.config import config

class EmailProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "email_queue"

    async def connect(self):
        self.connection = await connect_robust(**config.rabbitmq_params)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name)

    async def send_email_task(self, to_email: str, subject: str, body: str):
        if not self.connection:
            await self.connect()
            
        message = {
            "to_email": to_email,
            "subject": subject,
            "body": body
        }
        
        await self.channel.default_exchange.publish(
            Message(json.dumps(message).encode()),
            routing_key=self.queue_name
        )
```

RabbitMQ consumer для обработки задач
```python
import json
import asyncio
from aio_pika import connect_robust
from app.core.config import config
from app.core.services.email import EmailService

class EmailConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "email_queue"
        self.email_service = EmailService()

    async def connect(self):
        self.connection = await connect_robust(**config.rabbitmq_params)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name)

    async def process_message(self, message):
        async with message.process():
            body = json.loads(message.body.decode())
            await self.email_service.send_email(
                to_email=body["to_email"],
                subject=body["subject"],
                body=body["body"]
            )

    async def run(self):
        if not self.connection:
            await self.connect()
            
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.process_message(message)
```

Пример ручки:
```python
from fastapi import APIRouter, Depends
from app.core.services.email_producer import EmailProducer

router = APIRouter()
producer = EmailProducer()

@router.post("/send-email")
async def send_email(to_email: str, subject: str, body: str):
    await producer.send_email_task(to_email, subject, body)
    return {"status": "Email поставлен в очередь"}
```

Параметры:

- `smtp_server` - твой почтовый домен mail.ebtest.ru
- `smtp_port` - 587 для TLS
- `sender_email` - адрес с которого будут уходить письма
- `smtp_password` - пароль от почтового ящика noreply@ebtest.ru

```python
class Settings(BaseSettings):
    smtp_server: str = Field("mail.ebtest.ru", description="SMTP сервер")
    smtp_port: int = Field(587, description="SMTP порт") 
    sender_email: str = Field("noreply@ebtest.ru", description="Email отправителя")
    smtp_password: SecretStr
```

Для деплоя docker-compose.mail.yml:
```уaml
services:
  mailserver:
    image: stalwartlabs/mail-server:latest
    container_name: stalwart-mail
    ports:
      - "25:25"     # SMTP
      - "587:587"   # SMTP с TLS
      - "465:465"   # SMTP SSL
      - "143:143"   # IMAP
      - "993:993"   # IMAP SSL
      - "8080:8080" # Веб-интерфейс
    volumes:
      - ./mail_data:/opt/stalwart-mail
    restart: unless-stopped
    networks:
      - app_network

networks:
  app_network:
    name: app_network
```

### Настройки записей в DNS:
Для настройки MX записи для Stalwart нужно:

В поле Subdomain: оставляем "@" (это значит для всего домена ebtest.ru)
Priority: 10 (норм значение)
Mail Server: укажи "mail.ebtest.ru." (точка в конце важна!)
Это значит, что вся почта для адресов вида *@ebtest.ru будет обрабатываться сервером mail.ebtest.ru

Теперь Stalwart сможет принимать письма для твоего домена. Осталось только настроить остальные DNS записи (DKIM, SPF, DMARC)

Для TXT записей нужно добавить:

SPF для домена:
Subdomain: "@" (или оставить пустым)
Text: "v=spf1 mx -all ra=postmaster"

SPF для mail:
Subdomain: "mail"
Text: "v=spf1 a -all ra=postmaster"

DMARC:
Subdomain: "_dmarc"
Text: "v=DMARC1; p=reject; rua=mailto:postmaster@ebtest.ru; ruf=mailto:postmaster@ebtest.ru"

DKIM (две записи):
Subdomain: "202404e._domainkey"
Text: [значение из Stalwart]

Subdomain: "202404r._domainkey"
Text: [значение из Stalwart]

Два последних, как пример, делается один (ниже).

### Настройки почтового сервера:
В Settings > Signatures > DKIM Signing создай новую сигнатуру:

Signature ID: ebtest (или любое другое имя)
Algorithm: Ed25519 SHA-256 (самый современный)
Domain Name: ebtest.ru
Selector: mail (или любой другой, это часть DNS записи)
Headers: From, To, Subject, Date (основные)
Canonicalization: Relaxed/Relaxed
Key: [тут сгенерируется приватный ключ]

Нужно настроить еще несколько важных разделов:

SMTP -> Outbound:
Добавить порт 587 для TLS
Настроить аутентификацию
Authentication:
Создать пользователя noreply@ebtest.ru с паролем
Настроить права на отправку
Security:
Включить TLS
Настроить сертификаты
DMARC и SPF:
Включить проверки
Настроить политики
Spam filter:
Включить базовую защиту
Добавить белые списки

Генерирация Ed25519 ключа! Вот команда:
```bash
openssl genpkey -algorithm Ed25519 -out private.pem
```

Потом:
```bash
openssl pkey -in private.pem -pubout -out public.pem
```


Приватный ключ из private.pem вставляешь в поле Private Key в Stalwart.

А публичный из public.pem пойдет в DNS TXT запись, которую Stalwart сам сформирует после сохранения настроек.

Или можешь использовать онлайн генератор Ed25519 ключей, если лень возиться с openssl.

TXT запись в DNS
```
mail._domainkey.ebtest.ru TXT "v=DKIM1; k=ed25519; p=<your_public_key>"
```


`. Основные почтовые записи:
- DMARC для защиты от спуфинга
- SPF для разрешенных отправителей
- DKIM для цифровой подписи
- MX для маршрутизации почты

2. A-записи для сервисов:
- mail.ebtest.ru - почтовый сервер
- api.ebtest.ru - API
- dev.ebtest.ru - разработка
- grafana.ebtest.ru - мониторинг
- rabbitmq.ebtest.ru - очереди


Без TLS сертификатов почтовый сервер не заработает нормально.

В разделе Server -> TLS нужно:

Получить Let's Encrypt сертификат для mail.ebtest.ru
Включить STARTTLS для SMTP
Настроить DANE/MTA-STS для безопасности
Давай сначала поставим сертификат, тогда и остальные функции станут доступны. Почтовые сервера без TLS сейчас считаются небезопасными и письма от них часто попадают в спам.

Как получить сертификат:

Включи ACME в настройках
Добавь mail.ebtest.ru в список доменов
Выбери challenge type (http или dns)
Дождись выпуска сертификата
После этого можно будет настраивать AI и другие крутые фичи! 

Stalwart может использовать AI для:

Классификации спама
Анализа содержимого писем
Автоматических ответов
Можешь подключить:

OpenAI API (GPT)
Свою локальную модель
Любой другой AI endpoint
Настройка:

Type: Chat Completion
Endpoint URL: URL твоей модели или api.openai.com
API token: твой ключ доступа
Timeout: 30 seconds (чтоб не тормозило)

В ACME настраиваем:
Directory Id: letsencrypt
ACME provider: Let's Encrypt
Directory URL: https://acme-v02.api.letsencrypt.org/directory
Challenge type: TLS-ALPN-01 (самый надежный для почтовых серверов)
Contact Email: admin@ebtest.ru
Subject names: mail.ebtest.ru
Renew before: 30 days
После сохранения Stalwart автоматически запросит сертификат у Let's Encrypt.