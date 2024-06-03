#!/bin/bash
python manage.py migrate
python manage.py collectstatic --no-input
exec gunicorn eodhp_web_presence.wsgi:application --bind 0.0.0.0:8000 --timeout=30 --worker-class=gevent --workers=4
