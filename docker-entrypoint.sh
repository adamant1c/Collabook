#!/bin/bash
set -e

echo "🚀 Starting Django frontend..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
max_attempts=30
attempt=0

until PGPASSWORD=$DB_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ Database connection timeout after ${max_attempts} attempts"
    exit 1
  fi
  echo "Database is unavailable - sleeping (attempt $attempt/$max_attempts)"
  sleep 2
done
echo "✅ Database is ready!"

# Run migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Compile translations
echo "🌍 Compiling translations..."
python manage.py compilemessages --ignore=venv 2>/dev/null || true

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Django initialization complete!"
echo "🎮 Starting Gunicorn with $@ ..."

# Execute the command passed to docker (gunicorn)
exec "$@"
