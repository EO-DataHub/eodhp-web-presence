#!/bin/bash

check_webpack_ready() {
    echo "Checking for webpack-stats.json..."
    for i in {1..10}; do
        if [ -f "/app/webpack-stats.json" ]; then
            echo "webpack-stats.json found. Proceeding..."
            return 0
        else
            echo "Waiting for webpack-stats.json to become available..."
            sleep 2
        fi
    done
    echo "Failed to find webpack-stats.json. Exiting..."
    exit 1
}

if [ "$DJANGO_ENV" == "development" ]; then
    # Wait for webpack to be ready
    check_webpack_ready
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py migrate
    python manage.py collectstatic --no-input
    exec gunicorn eodhp_web_presence.wsgi:application --bind 0.0.0.0:8000 --timeout=30 --worker-class=gevent --workers=4
fi
