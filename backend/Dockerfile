FROM python:3.12-slim
ENV DEBIAN_FRONTEND='noninteractive'
RUN apt-get update && apt install -y curl libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH="${PATH}:/root/.local/bin"
COPY ./src /backend/src
COPY migration /backend/migration
COPY alembic.ini /backend/
COPY pyproject.toml /backend/
ENV PYTHONPATH /backend/src
WORKDIR /backend
RUN poetry config virtualenvs.create false \
    && poetry install --no-root
RUN chmod +x ./src/start.sh
EXPOSE 8000