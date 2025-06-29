#!/bin/bash
# entrypoint.sh

# Run Django in background
python manage.py runserver 0.0.0.0:8000 &

# Run FastAPI service in foreground (to keep container alive)
python fastapi_services/embedding_service.py
