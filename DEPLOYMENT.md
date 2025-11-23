# Production Deployment Guide 🚀

## Overview

Complete guide for deploying Collabook RPG to production.

---

## Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Docker & Docker Compose installed
- Domain name with DNS configured
- SSL certificate (Let's Encrypt)

---

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

---

## Step 2: Clone Repository

```bash
# Clone project
git clone https://github.com/your-repo/collabook.git
cd collabook
```

---

## Step 3: Environment Configuration

### Generate SECRET_KEY

```bash
openssl rand -hex 32
# Example: a1b2c3d4e5f6789...
```

### Create Production `.env`

```ini
# Security (CRITICAL!)
SECRET_KEY=your-generated-secret-key-here
ENVIRONMENT=production

# LLM Provider (Choose ONE)
GEMINI_API_KEY=your-gemini-api-key-here

# Database
DATABASE_URL=postgresql://collabook:STRONG_PASSWORD@db:5432/collabook_db
POSTGRES_PASSWORD=STRONG_PASSWORD

# Redis
REDIS_URL=redis://redis:6379/0

# Content Moderation
CONTENT_FILTER_LEVEL=moderate
LOG_VIOLATIONS=true

# Localization
LANGUAGE=en
```

---

## Step 4: Deploy

```bash
# Build and start services
docker compose up --build -d

# Initialize database
docker compose exec backend python manage.py create-admin
docker compose exec backend python manage.py seed-worlds
docker compose exec backend python manage.py seed-quests
docker compose exec backend python manage.py seed-enemies
docker compose exec backend python manage.py seed-items
```

---

## Security Checklist ✅

- [ ] SECRET_KEY is strong (32+ chars, random)
- [ ] ENVIRONMENT=production
- [ ] Database password is strong
- [ ] HTTPS/SSL enabled
- [ ] Content filter enabled
- [ ] Backups automated

---

## Cost Estimation 💰

**Monthly** (50 active users): €13-29/month

---

*Epic adventures await! ⚔️🎲*
