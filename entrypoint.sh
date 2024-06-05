#!/bin/bash

if [ "$DJANGO_ENV" == "development" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py migrate
    python manage.py collectstatic --no-input
    exec gunicorn eodhp_web_presence.wsgi:application --bind 0.0.0.0:8000 --timeout=30 --worker-class=gevent --workers=4
fi
