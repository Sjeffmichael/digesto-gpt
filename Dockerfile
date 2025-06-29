FROM python:3.10.16-slim

# Python
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_INSTALLER_MAX_WORKERS=4 \
    POETRY_REQUESTS_MAX_RETRIES=10 \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

RUN pip3 install --upgrade pip
RUN apt-get update && apt-get install -y curl gettext && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry is on PATH
ENV PATH="${POETRY_HOME}/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-directory --no-root

COPY . /app

# Collect static files
RUN python manage.py collectstatic --noinput

RUN chmod +x startup.sh
