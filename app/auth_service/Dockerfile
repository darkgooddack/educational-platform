FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src /app/src
COPY ./scripts/start.sh /app/scripts/start.sh
COPY alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations
COPY .env /app/.env

RUN chmod +x /app/scripts/start.sh

ENV PYTHONPATH="/app"

CMD ["/app/scripts/start.sh"]