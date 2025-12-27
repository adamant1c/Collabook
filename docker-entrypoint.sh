#!/bin/bash
set -e

echo "🚀 Starting Django frontend..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
max_attempts=60
attempt=0

until psql "$DATABASE_URL" -c '\q' 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Database connection timeout after ${max_attempts} attempts"
        exit 1
    fi
    echo "Database is unavailable - sleeping (attempt $attempt/$max_attempts)"
    sleep 2
done

echo "✅ Database is ready!"

# The rest remains the same
echo "📊 Running database migrations..."
python manage.py migrate --noinput

echo "🌍 Compiling translations..."
python manage.py compilemessages --ignore=venv 2>/dev/null || true

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Django initialization complete!"

echo "🎮 Starting Gunicorn with $@ ..."
exec "$@"