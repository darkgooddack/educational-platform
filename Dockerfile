FROM python:3.11.11-alpine3.19

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update
RUN apk add -v --no-cache --virtual .build-deps gcc
RUN apk add -v --no-cache --virtual .build-deps python3-dev
RUN apk add -v --no-cache --virtual .build-deps musl-dev
RUN apk add -v --no-cache --virtual .build-deps postgresql16-dev
RUN apk add -v --no-cache postgresql16-client
RUN apk add -v --no-cache libpq
RUN apk add -v --no-cache poppler-utils

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8000

COPY . /usr/src/app/

RUN uv sync --frozen --no-cache

RUN chmod +x /usr/src/app/docker-entrypoint.sh

ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]
