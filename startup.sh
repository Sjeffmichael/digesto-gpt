#!/bin/bash
# entrypoint.sh

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Compiling translations..."
django-admin compilemessages --ignore=env

echo "Starting Django server in background..."
python manage.py runserver 0.0.0.0:8000 &

echo "Starting FastAPI embedding service..."
exec python -m fastapi_services.embedding_service
