FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx

# Установка poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Копируем зависимости
COPY pyproject.toml poetry.lock* /backend/
WORKDIR /backend

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Копируем остальные файлы
COPY ./src /backend/src
COPY ./src/start.sh /backend/src/start.sh
COPY migration /backend/migration
COPY alembic.ini /backend/

RUN chmod +x /backend/src/start.sh

ENV PYTHONPATH=/backend/src

EXPOSE 8000
