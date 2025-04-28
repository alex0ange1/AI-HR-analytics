#!/bin/sh

SCRIPT_DIR=$(dirname "$0")

echo "Running in directory: $SCRIPT_DIR"  # Логирование текущей директории
echo "Running alembic upgrade head"
alembic upgrade head

echo "Running main.py"
python "${SCRIPT_DIR}/main.py"
