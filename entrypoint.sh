#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --noinput

CPU_COUNT=$(nproc)
WORKERS=$((2 * CPU_COUNT + 1))

echo "Starting Django server with $WORKERS workers..."
exec gunicorn --workers "$WORKERS" --bind 0.0.0.0:8000 UA_13XX_bravo.wsgi:application