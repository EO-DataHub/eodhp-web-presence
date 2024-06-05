#!/bin/bash

check_webpack_ready() {
    echo "Checking for webpack-stats.json..."
    for i in {1..10}; do
        if [ -f "/app/webpack-stats.json" ]; then
            echo "webpack-stats.json found. Proceeding..."
            sleep 8
            return 0
        else
            echo "Waiting for webpack-stats.json to become available..."
            sleep 2
        fi
    done
    echo "Failed to find webpack-stats.json. Exiting..."
    exit 1
}

run_django_prereqs() {
    echo "Running Django prerequisites..."
    python manage.py migrate
    python manage.py collectstatic --no-input
}

if [ "$DJANGO_ENV" == "development" ]; then
    # Wait for webpack to be ready
    check_webpack_ready
    # Run Django prerequisites
    run_django_prereqs
    python manage.py runserver 0.0.0.0:8000
else
    run_django_prereqs
    exec gunicorn eodhp_web_presence.wsgi:application --bind 0.0.0.0:8000 --timeout=30 --worker-class=gevent --workers=4
fi
