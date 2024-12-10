#!/bin/bash

# Collect static files
echo "Collect static files"
poetry run python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
poetry run python manage.py migrate

# Start server
echo "Starting server"
poetry run daphne -b 0.0.0.0 -p 8080 dosac.asgi:application