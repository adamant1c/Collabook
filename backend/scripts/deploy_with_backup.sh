#!/bin/bash
set -e

# Detect if running inside container or on host
if [ -f /.dockerenv ]; then
    # Running inside container - cannot use docker compose commands
    echo "❌ ERROR: This script must be run from the HOST, not inside a container."
    echo ""
    echo "Usage from host:"
    echo "  ./scripts/deploy_with_backup.sh"
    echo ""
    exit 1
fi

echo ""
echo "Service options:"
echo "  1) Development"
echo "  2) Production"
echo ""
read -p "Choose an option [1/2]: " EXPORT_CHOICE_OP

if [[ "$EXPORT_CHOICE_OP" == "1" ]]; then
    echo "Implementing Development:"
    COMPOSE="docker compose -f docker-compose.yml"
elif [[ "$EXPORT_CHOICE_OP" == "2" ]]; then
    echo "Implementing Production:"
    COMPOSE="docker compose -f docker-compose.prod.yml"
else
    echo "❌ Invalid choice. Aborting."
fi

EXPORT_DIR="backend/data/exports"

echo "🚀 Safe deploy with optional DB export"
echo "--------------------------------------"

# --------------------------------------------------
# 0. Sanity checks
# --------------------------------------------------
if [ ! -d "$EXPORT_DIR" ]; then
  mkdir -p "$EXPORT_DIR"
fi

# --------------------------------------------------
# 1. Ask operator what to do with exports
# --------------------------------------------------
echo ""
echo "📦 Database export options:"
echo "  1) Export CURRENT database to JSON (overwrite existing files)"
echo "  2) Use EXISTING JSON files in data/exports"
echo ""
read -p "Choose an option [1/2]: " EXPORT_CHOICE

if [[ "$EXPORT_CHOICE" == "1" ]]; then
    echo "📤 Exporting live database to JSON..."
    $COMPOSE exec backend python scripts/export_data.py
elif [[ "$EXPORT_CHOICE" == "2" ]]; then
    echo "📂 Using existing JSON files in $EXPORT_DIR"
    if [ -z "$(ls -A $EXPORT_DIR)" ]; then
        echo "❌ ERROR: $EXPORT_DIR is empty. Cannot continue."
        exit 1
    fi
else
    echo "❌ Invalid choice. Aborting."
    exit 1
fi

# --------------------------------------------------
# 2. Confirmation before destructive action
# --------------------------------------------------
echo ""
echo "⚠️  WARNING:"
echo "This operation will:"
echo "  - STOP all containers"
echo "  - DELETE the PostgreSQL database"
echo "  - REBUILD all images"
echo ""
read -p "Type 'Y' to continue: " CONFIRM

if [[ "$CONFIRM" != "Y" ]]; then
    echo "❌ Operation cancelled by user."
    exit 0
fi

# --------------------------------------------------
# 3. Complete cleanup: containers, volumes, and orphans
# --------------------------------------------------
echo ""
echo "🛑 Stopping containers and removing volumes..."
$COMPOSE down -v --remove-orphans

echo "🧹 Cleaning up orphaned volumes..."
docker volume prune -f

echo "🗑️  Removing postgres volume if it exists..."
docker volume rm collabook_postgres_data 2>/dev/null || echo "   (Volume already removed)"

echo "✓ Complete cleanup done"

# --------------------------------------------------
# 4. Pull latest code
# --------------------------------------------------
echo ""
echo "📥 Pulling latest code from git..."
git pull || echo "   ⚠️  Warning: git pull failed (possibly no upstream tracking). Continuing with existing local code."

# --------------------------------------------------
# 5. Rebuild & start (1 backend only)
# --------------------------------------------------
echo ""
echo "🏗 Rebuilding containers..."
$COMPOSE up -d --build --scale backend=1

echo "⏳ Waiting for backend to be ready..."
sleep 25

# --------------------------------------------------
# 6. Database is already created by postgres init
# --------------------------------------------------
echo ""
echo "🧱 Initializing database schema..."
$COMPOSE exec backend python manage.py init-db

# --------------------------------------------------
# 6.5. Run migrations if any exist
# --------------------------------------------------
echo ""
echo "🔄 Running database migrations (if any)..."
MIGRATION_DIR="backend/migrations"

if [ -d "$MIGRATION_DIR" ] && [ -n "$(ls -A $MIGRATION_DIR/*.py 2>/dev/null)" ]; then
    echo "📋 Found migration scripts in $MIGRATION_DIR"
    for migration_script in $MIGRATION_DIR/*.py; do
        if [ -f "$migration_script" ]; then
            script_name=$(basename "$migration_script")
            echo "   ⚙️  Running: $script_name"
            $COMPOSE exec backend python "migrations/$script_name" || echo "   ⚠️  Migration $script_name failed (may be already applied)"
        fi
    done
    echo "✓ All migrations processed"
else
    echo "   ℹ️  No migrations found, skipping..."
fi

# --------------------------------------------------
# 6.6. Compile translations
# --------------------------------------------------
echo ""
echo "🌐 Compiling translations..."
$COMPOSE exec frontend python manage.py compilemessages || echo "   ⚠️  Could not compile messages (gettext might not be installed)"

# --------------------------------------------------
# 7. Seed or Import database
# --------------------------------------------------
echo ""
echo "🌍 Populating database..."

if [[ "$EXPORT_CHOICE" == "1" ]] || [[ -f "$EXPORT_DIR/users.json" ]]; then
    # Import from JSON if we have exported data
    echo "📥 Importing data from JSON exports..."
    $COMPOSE exec backend python scripts/import_data.py
else
    # Use seed commands for fresh setup
    echo "🌱 Seeding with default data..."
    $COMPOSE exec backend python manage.py seed-worlds
    $COMPOSE exec backend python manage.py seed-quests
    $COMPOSE exec backend python manage.py seed-enemies
    $COMPOSE exec backend python manage.py seed-npcs || true
    $COMPOSE exec backend python manage.py seed-items || true
    $COMPOSE exec backend python manage.py seed-maps || true
fi

# --------------------------------------------------
# 7.5. Reset PostgreSQL sequences to avoid duplicate key errors
# --------------------------------------------------
echo ""
echo "🔑 Resetting PostgreSQL sequences..."
$COMPOSE exec frontend python manage.py shell -c "
from io import StringIO
from django.core.management import call_command
from django.apps import apps
from django.db import connection

app_labels = [a.label for a in apps.get_app_configs()]
buf = StringIO()
call_command('sqlsequencereset', *app_labels, stdout=buf, no_color=True)
sql = buf.getvalue().strip()
if sql:
    with connection.cursor() as cursor:
        cursor.execute(sql)
    print(f'✓ Sequences reset successfully ({sql.count(chr(59))} statements)')
else:
    print('ℹ️  No sequences to reset')
" || echo "   ⚠️  Could not reset sequences (non-critical)"

# --------------------------------------------------
# 8. Create superuser for development
# --------------------------------------------------
if [[ "$EXPORT_CHOICE_OP" == "1" ]]; then
    echo ""
    echo "👤 Creating admin user 'adm1n' for development..."
    $COMPOSE exec backend python scripts/create_admin.py
fi

# --------------------------------------------------
# 8. Scale backend (only in production)
# --------------------------------------------------
if [[ "$EXPORT_CHOICE_OP" == "2" ]]; then
    echo ""
    echo "⚡ Scaling backend to 4 replicas (Production)..."
    $COMPOSE up -d --scale backend=4
else
    echo ""
    echo "ℹ️  Development mode: keeping 1 backend instance"
fi

echo ""
echo "✅ Deploy completed successfully!"

# --------------------------------------------------
# 9. Run Regression Tests
# --------------------------------------------------
echo ""
echo "🧪 Running Regression Tests..."

# Create a temporary virtual environment for tests to avoid polluting the host
if [ ! -d "test/venv" ]; then
    python3 -m venv test/venv
fi

# Activate venv and install requirements
source test/venv/bin/activate
pip install -r test/requirements.txt -q

# Set environment variable based on user choice
if [[ "$EXPORT_CHOICE_OP" == "1" ]]; then
    export TEST_ENV="dev"
elif [[ "$EXPORT_CHOICE_OP" == "2" ]]; then
    # Give production containers a few seconds to fully boot and register with nginx
    echo "⏳ Waiting a moment for production services to stabilize..."
    sleep 10
    export TEST_ENV="prod"
fi

# Run pytest
echo "🚀 Executing pytest suite..."
pytest test/ -v

TEST_EXIT_CODE=$?
deactivate

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "❌ WARNING: Regression tests failed! The deployed application may have issues."
    exit 1
else
    echo "✅ Regression tests passed successfully!"
fi
