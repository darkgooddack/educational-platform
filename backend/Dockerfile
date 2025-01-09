FROM python:3.11.11-alpine3.21

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && apk add --no-cache \
    postgresql-client \
    libpq \
    poppler-utils

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

EXPOSE 8000
# При нынешней структуре приходится использовать директорию backend внутри контейнера, чтобы не было проблем с импортами
COPY . ./backend

COPY ./docker-entrypoint.sh /usr/src/app/backend/docker-entrypoint.sh
RUN chmod +x /usr/src/app/backend/docker-entrypoint.sh

ENTRYPOINT ["sh", "/usr/src/app/backend/docker-entrypoint.sh"]
