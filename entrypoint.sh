#!/bin/bash

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Start Gunicorn
exec gunicorn eodhp_web_presence.wsgi:application --bind 0.0.0.0:8000 --timeout=30 --worker-class=gevent --workers=4
