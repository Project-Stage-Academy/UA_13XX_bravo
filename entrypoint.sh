#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate --no-input

echo "Loading initial data..."
python manage.py loaddata notifications/fixtures/type_fixture.json

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Daphne ASGI server..."
exec daphne -b 0.0.0.0 -p 8000 UA_13XX_bravo.asgi:application