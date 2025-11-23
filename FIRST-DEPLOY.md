# 🚀 First Deployment - Step by Step Guide

## ✅ System Check Complete

- Docker: 29.0.2 ✅
- Docker Compose: v2.40.3 ✅  
- .env file: Found ✅

---

## 📋 Deployment Steps

### Step 1: Clean Start (Recommended)

```bash
# Stop any running containers
docker compose down -v

# Remove old volumes (fresh start)
docker volume prune -f
```

---

### Step 2: Build and Start Services

```bash
# Build and start all services
docker compose up --build -d

# This will start:
# - PostgreSQL database
# - Redis cache
# - Backend (FastAPI)
# - Frontend (Streamlit)
```

**Expected output:**
```
[+] Building...
[+] Running 5/5
 ✔ Network collabook_default      Created
 ✔ Container collabook-db-1       Started
 ✔ Container collabook-redis-1    Started
 ✔ Container collabook-backend-1  Started
 ✔ Container collabook-frontend-1 Started
```

---

### Step 3: Verify Services

```bash
# Check if all containers are running
docker compose ps

# Expected: 4 containers in "Up" state
```

---

### Step 4: Initialize Database

```bash
# 1. Create admin user
docker compose exec backend python manage.py create-admin
# Enter:
# - Username: admin
# - Password: admin123 (or your choice)
# - Email: admin@collabook.local
# - Name: Game Master

# 2. Seed worlds
docker compose exec backend python manage.py seed-worlds
# Creates: Historical, Fantasy, Sci-Fi worlds

# 3. Seed quests
docker compose exec backend python manage.py seed-quests
# Creates: 6 quests (2 per world)

# 4. Seed enemies
docker compose exec backend python manage.py seed-enemies
# Creates: 9 enemies (3 per world)

# 5. Seed items
docker compose exec backend python manage.py seed-items
# Creates: 9 items (food, water, potions)
```

---

### Step 5: Access Application

**Frontend (Player Interface)**:
- URL: http://localhost:8501
- Register new account
- Start playing!

**Backend API**:
- URL: http://localhost:8000
- Docs: http://localhost:8000/docs

---

### Step 6: First Login & Test

1. Open http://localhost:8501
2. Click "Register" tab
3. Create account:
   - Username: testplayer
   - Email: test@example.com
   - Password: password123
   - Name: Test Hero
   - Profession: Warrior
4. Choose world (try Fantasy)
5. Take first action: "I explore the castle"
6. Watch AI narrate your adventure!

---

## 🧪 Verify Everything Works

```bash
# Check logs
docker compose logs backend | tail -20
docker compose logs frontend | tail -20

# Test backend API
curl http://localhost:8000/

# Should return:
# {"message":"Collabook API","version":"2.1.0"}
```

---

## 🎮 Quick Test Checklist

- [ ] All 4 containers running
- [ ] Admin user created
- [ ] Worlds seeded (3 worlds)
- [ ] Quests seeded (6 quests)
- [ ] Enemies seeded (9 enemies)
- [ ] Items seeded (9 items)
- [ ] Can access frontend (http://localhost:8501)
- [ ] Can register new user
- [ ] Can select world
- [ ] Can take action and get narration
- [ ] Can see stats in sidebar

---

## 🐛 Troubleshooting

### Backend won't start
```bash
docker compose logs backend
# Check for SECRET_KEY errors
```

### Database connection error
```bash
docker compose restart db
docker compose restart backend
```

### Frontend blank page
```bash
docker compose logs frontend
docker compose restart frontend
```

### Clear everything and restart
```bash
docker compose down -v
docker volume prune -f
docker compose up --build -d
# Then run initialization steps again
```

---

## 🎉 Success!

If you can:
1. ✅ Access http://localhost:8501
2. ✅ Register and login
3. ✅ See your stats in sidebar
4. ✅ Take actions and get narration

**Your Collabook RPG is live!** ⚔️🎲

---

## 📊 Next Steps

- Test combat system (take ~20 actions, encounter triggers)
- Complete a quest
- Try survival mechanics (hunger/thirst deplete over time)
- Test content filter (try inappropriate input)
- Add character portraits (see CHARACTER-PORTRAITS.md)
- Invite friends to play!

---

*Ready for epic adventures!* 🎮✨
