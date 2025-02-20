from email.mime.text import MIMEText
import smtplib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.messaging import EmailProducer
from app.core.config import config

class EmailService:
    def __init__(self):
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.sender_email = config.sender_email
        self.password = config.smtp_password.get_secret_value()

        template_dir = Path(__file__).parents[3] / 'templates' / 'email'
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
    async def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = to_email

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.password)
            server.send_message(msg)

    async def send_verification_email(self, to_email: str, user_name: str, verification_token: str):
        template = self.env.get_template('verification.html')
        verification_url = f"http://localhost:8000/api/v1/auth/verify-email/{verification_token}"

        html_content = template.render(
            user_name=user_name,
            verification_url=verification_url
        )

        producer = EmailProducer()
        await producer.send_email_task(
            to_email=to_email,
            subject="Подтверждение email адреса",
            body=html_content
        )
