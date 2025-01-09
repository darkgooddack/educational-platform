FROM python:3.11.11-alpine3.21

WORKDIR /usr/src/

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

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8001

COPY . /usr/src/

RUN uv sync --frozen --no-cache

COPY ./docker-entrypoint.sh /usr/src/docker-entrypoint.sh
RUN chmod +x /usr/src/docker-entrypoint.sh

ENTRYPOINT ["sh", "/usr/src/docker-entrypoint.sh"]
