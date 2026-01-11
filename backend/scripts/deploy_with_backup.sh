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
read -p "Choose an option [1/2]: " EXPORT_CHOICE

if [[ "$EXPORT_CHOICE" == "1" ]]; then
    echo "Implementing Development:"
    COMPOSE="docker compose -f docker-compose.yml"
elif [[ "$EXPORT_CHOICE" == "2" ]]; then
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
read -p "Type 'YES' to continue: " CONFIRM

if [[ "$CONFIRM" != "YES" ]]; then
    echo "❌ Operation cancelled by user."
    exit 0
fi

# --------------------------------------------------
# 3. Complete cleanup: containers, volumes, and orphans
# --------------------------------------------------
echo ""
echo "🛑 Stopping containers and removing volumes..."
$COMPOSE down -v

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
git pull

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
    $COMPOSE exec backend python manage.py seed-items || true
fi

# --------------------------------------------------
# 8. Scale backend
# --------------------------------------------------
echo ""
echo "⚡ Scaling backend to 4 replicas..."
$COMPOSE up -d --scale backend=4

echo ""
echo "✅ Deploy completed successfully!"
