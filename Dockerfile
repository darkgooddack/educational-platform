FROM python:3.11.11-alpine3.19

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql16-dev

RUN apk add --no-cache \
    postgresql16-client \
    libpq \
    poppler-utils

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8000

COPY . /usr/src/app/

RUN uv sync --frozen --no-cache

RUN chmod +x /usr/src/app/docker-entrypoint.sh

ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]
