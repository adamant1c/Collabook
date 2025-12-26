#!/bin/bash

# Default to production if not specified
ENVIRONMENT=${ENVIRONMENT:-production}
PORT=${PORT:-8501}

echo "Starting Django in $ENVIRONMENT mode on port $PORT..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

if [ "$ENVIRONMENT" = "development" ]; then
    # Start development server
    exec python manage.py runserver 0.0.0.0:$PORT
else
    # Start Gunicorn production server
    exec gunicorn collabook_frontend.wsgi:application \
        --bind 0.0.0.0:$PORT \
        --workers 3 \
        --access-logfile - \
        --error-logfile -
fi
