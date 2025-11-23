# Phase 1: Authentication System - Setup Guide

## ✅ What's Been Implemented

### Backend (Complete!)
- ✅ Database schema with auth fields
- ✅ Password hashing (bcrypt)
- ✅ JWT tokens (24h expiration)
- ✅ Registration endpoint
- ✅ Login endpoint
- ✅ Password reset (request + reset)
- ✅ Role-based access (Admin/Player)
- ✅ Admin CLI tool
- ✅ 3 default worlds seeder

### API Changes
- ✅ `/auth/register` - Register new player
- ✅ `/auth/login` - Login (returns JWT token)
- ✅ `/auth/me` - Get current user info
- ✅ `/auth/request-reset` - Request password reset
- ✅ `/auth/reset-password` - Reset password with token
- ✅ `/stories/*` - Now requires authentication
- ✅ `/stories/` POST - Requires ADMIN role

### Frontend
- ⏳ TODO (Phase 1B - next step)

---

## 🚀 Quick Start

### 1. Rebuild Containers (Fresh Database)

```bash
cd /home/alessandro/Project/Collabook

# Stop everything and delete old database
docker-compose down -v

# Rebuild with new dependencies
docker-compose up --build
```

Wait for all services to start. You should see:
```
backend-1   | ✓ Using Ollama (gemma3:latest) - 100% FREE & LOCAL
backend-1   | INFO:     Application startup complete
```

### 2. Create Admin User

In a new terminal:

```bash
# Enter backend container
docker-compose exec backend python manage.py create-admin

# Follow prompts:
# Username: admin
# Password: admin123
# Email: admin@collabook.local
# Name: Admin User
```

You should see:
```
✓ Admin user 'admin' created successfully!
  Email: admin@collabook.local
  Name: Admin User
  Role: admin
```

### 3. Seed Default Worlds

```bash
docker-compose exec backend python manage.py seed-worlds
```

You should see:
```
✓ Default worlds created successfully!

  1. Echoes of the Past (Historical)
  2. Realm of Eternal Magic (Fantasy)
  3. Horizon Beyond Stars (Sci-Fi)
```

### 4. List Users (Verify)

```bash
docker-compose exec backend python manage.py list-users
```

---

## 🧪 Testing with curl

### Register a Player

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "player1",
    "email": "player1@test.com",
    "password": "password123",
    "name": "Elara the Brave",
    "profession": "Wandering Mage",
    "description": "A curious mage seeking adventure"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token!** Copy `access_token` value.

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=player1&password=password123"
```

### Get Current User

```bash
# Replace YOUR_TOKEN with the access_token from above
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": "abc123",
  "username": "player1",
  "email": "player1@test.com",
  "role": "player",
  "name": "Elara the Brave",
  "profession": "Wandering Mage",
  "level": 1,
  "xp": 0,
  ...
}
```

### List Worlds (Requires Auth)

```bash
curl http://localhost:8000/stories/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Should show 3 default worlds!

### Try Creating World as Player (Should Fail!)

```bash
curl -X POST http://localhost:8000/stories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Custom World",
    "world_description": "A test world",
    "genre": "Adventure"
  }'
```

**Expected response:**
```json
{
  "detail": "Admin access required"
}
```

✅ Perfect! Role check working!

### Create World as Admin

First login as admin:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Copy the admin token, then:

```bash
curl -X POST http://localhost:8000/stories/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cyber Noir City",
    "world_description": "A dark cyberpunk metropolis",
    "genre": "Cyberpunk"
  }'
```

✅ Should work!

---

## 📊 Database Schema

### Users Table
- `id` - UUID
- `username` - Unique
- `email` - Unique, required
- `password_hash` - Bcrypt hashed
- `role` - ENUM: "admin" | "player"
- `name` - Character display name
- `profession`, `description`, `avatar_description`
- **RPG Stats** (Phase 2):
  - `hp`, `max_hp`, `strength`, `magic`, `dexterity`, `defense`
  - `xp`, `level`
- **Auth**:
  - `is_active` - Account enabled?
  - `last_login`
  - `reset_token`, `reset_token_expires`

### Stories Table
- `is_default` - TRUE for 3 predefined worlds
- `created_by` - User ID of creator (NULL for defaults)

### Characters Table (Updated)
- `hunger`, `thirst`, `fatigue` (Phase 5)
- `deaths`, `can_resurrect` (Phase 4)

---

## 🔐 Security Notes

✅ **Passwords**: Hashed with bcrypt (12 rounds)  
✅ **Tokens**: JWT with HS256, 24h expiration  
✅ **Reset Tokens**: Cryptographically secure, 1h expiration  
⚠️ **SECRET_KEY**: Change in `.env` for production!  
⚠️ **Email**: Currently prints to console (implement SMTP in production)  

---

## 🛠️ Admin CLI Commands

```bash
# All commands run inside backend container:
docker-compose exec backend python manage.py <command>

# Available commands:
create-admin     - Create a new admin user
list-users       - List all users
deactivate-user  - Deactivate a user account
init-db          - Initialize database tables
seed-worlds      - Create 3 default worlds
```

---

## ✅ Success Checklist

- [ ] `docker-compose up --build` runs without errors
- [ ] Admin user created via CLI
- [ ] 3 default worlds seeded
- [ ] Player can register (returns token)
- [ ] Player can login (returns token)
- [ ] `/auth/me` returns user data
- [ ] `/stories/` requires authentication
- [ ] Player CANNOT create worlds (403)
- [ ] Admin CAN create worlds (201)

---

## 🐛 Troubleshooting

### "Database connection error"
```bash
docker-compose down -v
docker-compose up --build
```

### "No LLM provider configured"
Check Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### "Failed to create admin"
Check for typos in username/email. List existing users:
```bash
docker-compose exec backend python manage.py list-users
```

---

## 📝 Next Steps

**Phase 1B** (Frontend):
- Login page
- Registration wizard
- Session management
- Password reset UI

**Phase 2**:
- Character creation wizard
- Stats initialization (random 1-10)
- Inventory system

Let me know when you're ready to test! 🚀
