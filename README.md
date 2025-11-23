# 🎲 Collabook RPG

**Collaborative storytelling RPG platform with AI-powered Dungeon Master**

Transform your creative ideas into epic adventures with friends! Collabook RPG combines collaborative storytelling with authentic D&D-style mechanics, intelligent AI narration, and a beautiful medieval-themed interface.

[![Version](https://img.shields.io/badge/version-2.1.0-gold.svg)](https://github.com/yourusername/collabook)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](#)

---

## ✨ Features

### � RPG Mechanics
- ⚔️ **D&D-Style Combat** - Dice rolls, initiative, critical hits
- 📊 **Character Progression** - 5 core stats, XP, level-ups
- 🎯 **Quest System** - Main & side quests with rewards
- � **Enemy Encounters** - Random battles with 9 enemy types
- 💰 **Loot & Rewards** - XP, gold, character growth
- 💀 **Death System** - Resurrection (1x) + permanent death

### 🤖 AI-Powered
- 📖 **Intelligent Narration** - Context-aware storytelling
- 🎲 **Dynamic World** - Adaptive responses to player actions
- **Token Optimized** - 70-85% cost reduction vs traditional approaches
- 💬 **Ollama Support** - Use local LLMs for development

### 🌍 World Building
- 🏰 **3 Default Worlds** - Historical, Fantasy, Sci-Fi
- 🛠️ **Custom Worlds** - Admin-created unique settings
- 📜 **Quest Editor** - Create and manage quests
- 👹 **Enemy Designer** - Configure combat challenges

### 🎨 Beautiful UI
- 🖼️ **Medieval Theme** - Parchment, gold, fantasy fonts
- 📱 **Responsive Design** - Desktop & mobile
- ✨ **Smooth Animations** - Glow effects, transitions
- 🎲 **Tabletop Feel** - Designed for board game fans

### 🔒 Security
- 🔐 **JWT Authentication** - Secure session management
- 🛡️ **Rate Limiting** - Prevent brute force attacks
- 👑 **Role-Based Access** - Admin & Player roles
- 📧 **Password Reset** - Email-based recovery

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** installed
- **Git** for cloning the repository
- **SECRET_KEY** for JWT (generated during setup)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/collabook.git
cd collabook
```

#### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate a secure SECRET_KEY (IMPORTANT!)
openssl rand -hex 32

# Edit .env and paste the SECRET_KEY
nano .env
```

**Update `.env` with your SECRET_KEY:**
```ini
SECRET_KEY=<paste-your-generated-key-here>
ENVIRONMENT=development

# LLM Configuration (choose one)
LLM_PROVIDER=ollama  # For local development
# LLM_PROVIDER=gemini  # For production
# GEMINI_API_KEY=your-api-key-here
```

#### 3. Build and Start Services

```bash
# Clean start (recommended for first time)
docker-compose down -v
docker-compose up --build
```

This will start:
- **Backend** (FastAPI) on `http://localhost:8000`
- **Frontend** (Streamlit) on `http://localhost:8501`
- **PostgreSQL** database on port `5432`
- **Redis** cache on port `6379`

#### 4. Initialize Database

In a new terminal, run these commands:

```bash
# Create admin user
docker-compose exec backend python manage.py create-admin
# Follow prompts to set username, password, email, name
# Example: admin / admin123 / admin@collabook.local / Game Master

# Seed default worlds (Historical, Fantasy, Sci-Fi)
docker-compose exec backend python manage.py seed-worlds

# Seed quests (6 default quests)
docker-compose exec backend python manage.py seed-quests

# Seed enemies (9 enemies across 3 worlds)
docker-compose exec backend python manage.py seed-enemies
```

#### 5. Access the Application

🎮 **Open your browser**: http://localhost:8501

**First Steps**:
1. Click "✨ Register" tab
2. Create your character (stats randomized automatically!)
3. Choose a world to explore
4. Start your adventure!

---

## 📋 Complete Setup Commands

For quick reference, here's the full command sequence:

```bash
# 1. Clone & Setup
git clone https://github.com/yourusername/collabook.git
cd collabook
cp .env.example .env

# 2. Generate SECRET_KEY
openssl rand -hex 32
# (Copy the output and paste into .env)

# 3. Edit .env file
nano .env
# Set SECRET_KEY=<generated-key>
# Save (Ctrl+O, Enter, Ctrl+X)

# 4. Start services
docker-compose down -v
docker-compose up --build

# 5. In new terminal - Initialize
docker-compose exec backend python manage.py create-admin
docker-compose exec backend python manage.py seed-worlds
docker-compose exec backend python manage.py seed-quests
docker-compose exec backend python manage.py seed-enemies

# 6. Open http://localhost:8501 🎮
```

---

## 🎮 How to Play

### 1. Character Creation
- Register with username, email, password
- Choose character name and profession
- Stats initialized randomly (1-10 per stat)
- Start at Level 1 with full HP

### 2. World Selection
- Choose from 3 default worlds:
  - **Echoes of the Past** - Historical medieval
  - **Realm of Eternal Magic** - High fantasy
  - **Horizon Beyond Stars** - Sci-fi future
- Or create custom worlds (admin only)

### 3. Gameplay Loop
1. **Take Actions** - Describe what you want to do
2. **AI Narrates** - DM responds with story continuation
3. **Random Encounters** - 15-30% chance of combat per turn
4. **Complete Quests** - Earn XP and gold rewards
5. **Level Up** - Grow stronger with each level

### 4. Combat System
- **Roll Initiative** - Dexterity-based turn order
- **Choose Action**:
  - ⚔️ **Attack** - 1d20 + STR modifier vs AC
  - ✨ **Magic** - 2d6 + MAG modifier (costs 5 MP)
  - 🛡️ **Defend** - +2 AC, damage reduced 50%
  - 🏃 **Flee** - DEX check to escape
- **Victory** - Earn XP and gold
- **Defeat** - First death: resurrect with penalty
- **Permanent Death** - Second death is final

### 5. Progression
- **Gain XP** from quests and combat
- **Level Up** automatically when threshold reached
- **Stats Increase** (+2-5 per stat on level up)
- **HP Restored** to full on level up

---

## 📸 Adding Character & Scene Images

### Overview

Enhance your storytelling with **character portraits** and **scene images**! The system automatically detects and displays images when characters or scenes are mentioned in the narration.

### Character Portraits

#### 📁 Location
```
frontend/assets/characters/
```

#### 📝 Naming Convention

**Format:** `npc_<CharacterName>.<extension>`

**Examples:**
```
npc_KingHarold.png       → "King Harold"
npc_DarkMage.jpg         → "Dark Mage"
npc_ElvenQueen.webp      → "Elven Queen"
npc_MerchantGiovanni.png → "Merchant Giovanni"
npc_GoblinScout.png      → "Goblin Scout"
```

**Rules:**
- Prefix: `npc_` (lowercase)
- Name: Remove spaces, capitalize each word (CamelCase)
- Extension: `.png`, `.jpg`, `.jpeg`, or `.webp`

#### 🎨 Image Specifications

| Property | Requirement |
|----------|-------------|
| **Format** | PNG, JPG, JPEG, or WebP |
| **Size** | Any (auto-resized to 512x512px) |
| **Aspect Ratio** | Any (centered with padding) |
| **Recommended** | Square images work best |

#### 🚀 How to Add

**Method 1: Manual (Direct Copy)**

```bash
# 1. Create or obtain character image
# 2. Name it following the convention
# 3. Copy to assets directory

cp your_character.png frontend/assets/characters/npc_KingHarold.png

# That's it! Image will be auto-resized to 512x512px
```

**Method 2: Admin Upload UI**

1. Login as admin
2. Navigate to "Character Gallery" tab
3. Click "Upload Portrait"
4. Enter character name (e.g., "King Harold")
5. Upload image (any size)
6. System automatically:
   - Formats filename → `npc_KingHarold.png`
   - Resizes to 512x512px
   - Optimizes for web

#### 🎭 How It Works

When the LLM narrates:

```
"King Harold welcomes you to the throne room. 
Beside him stands the Dark Mage."
```

Result:
```
┌──────────────────────────────┐
│ 👥 Characters in this Scene  │
│                              │
│  [King Harold]  [Dark Mage]  │
│   [Portrait]     [Portrait]  │
└──────────────────────────────┘
```

Automatically detects and displays portraits!

---

### Scene & Landscape Images

#### 📁 Location
```
frontend/assets/scenes/
```

#### 📝 Naming Convention

**Format:** `scene_<SceneName>.<extension>`

**Examples:**
```
scene_ThroneRoom.png         → "Throne Room"
scene_DarkForest.jpg         → "Dark Forest"
scene_SpaceStation.webp      → "Space Station"
scene_MountainPass.png       → "Mountain Pass"
scene_TavernInterior.jpg     → "Tavern Interior"
```

**Rules:**
- Prefix: `scene_` (lowercase)
- Name: Remove spaces, capitalize each word (CamelCase)
- Extension: `.png`, `.jpg`, `.jpeg`, or `.webp`

#### 🎨 Image Specifications

| Property | Requirement |
|----------|-------------|
| **Format** | PNG, JPG, JPEG, or WebP |
| **Size** | Any (auto-resized to fit) |
| **Aspect Ratio** | 16:9 recommended for landscapes |
| **Max Width** | Auto-limited to 1200px |

#### 🚀 How to Add

```bash
# Create scenes directory
mkdir -p frontend/assets/scenes

# Add your scene image
cp landscape.jpg frontend/assets/scenes/scene_DarkForest.jpg

# System will auto-detect when mentioned in narration!
```

#### 🌄 How It Works

When narration mentions a location:

```
"You enter the Dark Forest. The trees loom 
ominously overhead, blocking out the sunlight."
```

Result: Scene image displayed above the narration text!

---

### Complete Setup Example

```bash
# Navigate to project
cd /home/alessandro/Project/Collabook

# Create directories
mkdir -p frontend/assets/characters
mkdir -p frontend/assets/scenes

# Add character portraits
cp ~/images/king.png frontend/assets/characters/npc_KingHarold.png
cp ~/images/mage.jpg frontend/assets/characters/npc_DarkMage.jpg
cp ~/images/goblin.png frontend/assets/characters/npc_GoblinScout.png

# Add scene images
cp ~/images/throne_room.jpg frontend/assets/scenes/scene_ThroneRoom.jpg
cp ~/images/forest.png frontend/assets/scenes/scene_DarkForest.png
cp ~/images/tavern.jpg frontend/assets/scenes/scene_TavernInterior.jpg

# Rebuild frontend (images auto-resized on first use)
docker-compose restart frontend

# Done! Images will appear automatically in narration
```

---

### 🎨 Image Guidelines

#### Character Portraits

**Best Practices:**
- ✅ Square format (512x512 or similar)
- ✅ Character centered, facing forward
- ✅ Clear facial details
- ✅ Consistent art style across all characters
- ✅ Transparent background (PNG) or solid color

**Art Styles:**
- Fantasy character art (D&D style)
- Pixel art sprites
- AI-generated portraits (Stable Diffusion, Midjourney)
- Hand-drawn illustrations
- Photo portraits (for realistic settings)

**Tools:**
- AI: Stable Diffusion, Midjourney, DALL-E
- Manual: Photoshop, GIMP, Krita
- Online: Artbreeder, This Person Does Not Exist

#### Scene Images

**Best Practices:**
- ✅ Landscape format (16:9 aspect ratio)
- ✅ High quality but not huge (< 2MB)
- ✅ Matches world theme (medieval, fantasy, sci-fi)
- ✅ No text or UI elements
- ✅ Atmospheric and immersive

**Sources:**
- AI-generated (Midjourney, Stable Diffusion)
- Stock photos (Unsplash, Pexels - free)
- Game assets (with proper licenses)
- Custom artwork

---

### 🤖 LLM Integration

The system automatically:

1. **Scans** available character/scene images on startup
2. **Informs LLM** about available visuals via context
3. **Encourages use** of characters with portraits
4. **Detects mentions** in narration (case-insensitive)
5. **Displays automatically** when matched

**No manual triggers needed!**

---

### 📊 Performance

**Auto-Optimization:**
- ✅ Images resized to optimal dimensions
- ✅ File size compressed (quality 85%)
- ✅ Lazy loading (only when visible)
- ✅ Cached after first load

**Impact:**
- Character portrait: ~50-150KB each
- Scene image: ~100-300KB each
- Load time: ~50-200ms per image
- Total overhead: Minimal

---

### 🧪 Testing Your Images

```bash
# 1. Add test images
cp test_character.png frontend/assets/characters/npc_TestHero.png

# 2. Restart frontend
docker-compose restart frontend

# 3. In game, type action that mentions the character
"I look for Test Hero in the tavern"

# 4. If portrait appears → Success! ✅
# 5. If not → Check filename and format
```

**Debug Checklist:**
- [ ] File in correct directory (`frontend/assets/characters/`)
- [ ] Filename follows convention (`npc_Name.ext`)
- [ ] Format is supported (PNG/JPG/WEBP)
- [ ] Character name exactly matches narration (case-insensitive OK)
- [ ] Frontend restarted after adding image

---

### 💡 Pro Tips

1. **Batch Processing**: Use script to rename multiple files
   ```bash
   # Rename multiple character images
   for file in *.png; do
       name=$(basename "$file" .png)
       cp "$file" "frontend/assets/characters/npc_${name}.png"
   done
   ```

2. **Consistent Style**: Use same AI model/artist for all images

3. **Name Characters Distinctly**: Avoid generic names like "Guard" or "Merchant"
   - ✅ Good: "Captain Marcus", "Merchant Giovanni"
   - ❌ Bad: "The Guard", "A Merchant"

4. **Pre-generate Common NPCs**: Create portraits for:
   - Quest givers
   - Shop keepers
   - Important story characters
   - Recurring enemies/bosses

5. **Organize by World**: Optional subdirectories
   ```
   frontend/assets/characters/
   ├── historical/
   ├── fantasy/
   └── scifi/
   ```

---


## 🛠️ Management Commands

### CLI Tool: `manage.py`

```bash
# User Management
docker-compose exec backend python manage.py list-users
docker-compose exec backend python manage.py deactivate-user

# Database
docker-compose exec backend python manage.py init-db

# Content Seeding
docker-compose exec backend python manage.py seed-worlds
docker-compose exec backend python manage.py seed-quests
docker-compose exec backend python manage.py seed-enemies
```

---

## 🔧 Development

### Running Locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python manage.py init-db
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

**Database:**
```bash
# Start PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### Using Ollama (Local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Update .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
```

See [LOCAL-SETUP.md](LOCAL-SETUP.md) for detailed instructions.

---

## 📊 Architecture

```
Collabook/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── core/         # Database, security, LLM client
│   │   ├── models/       # SQLAlchemy & Pydantic models
│   │   ├── api/          # Endpoints (auth, stories, quests, combat)
│   │   └── agents/       # AI agents (narrator, world keeper)
│   ├── manage.py         # CLI management tool
│   └── requirements.txt
│
├── frontend/             # Streamlit application
│   ├── app.py           # Main application
│   ├── api_client.py    # Backend API client
│   ├── style.css        # RPG theme CSS
│   ├── ui_components.py # Custom UI components
│   └── requirements.txt
│
├── docker-compose.yml    # Development services
├── docker-compose.prod.yml  # Production config
└── .env.example         # Environment template
```

---

## 💰 Cost Optimization

### Token Usage (Optimized)

**Traditional Approach**: ~1500-2000 tokens/turn
**Collabook Optimized**: ~200-400 tokens/turn

**Savings**: 70-85% reduction! 🎯

### Estimated Costs (Monthly)

**50 Active Users, 100 turns/month each:**

| Provider | Traditional | Optimized | Savings |
|----------|------------|-----------|----------|
| Gemini Flash | ~$15 | ~$2 | **$13** |
| GPT-4 | ~$300 | ~$80 | **$220** |
| Ollama (Local) | $0 | $0 | Free! |

**Production Budget**: €10/month target ✅  
**Actual Cost**: ~€7/month (Hetzner + Gemini) ✅

---

## 🔒 Security Notes

### Before Production

1. **Change SECRET_KEY** in `.env` (minimum 32 chars)
2. **Update CORS** origins in `security_utils.py`
3. **Configure Email** service (SendGrid, AWS SES)
4. **Enable HTTPS** with Certbot
5. **Set up Monitoring** (Sentry, Prometheus)

### Security Features

- ✅ JWT authentication with 24h expiry
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Rate limiting on auth endpoints
- ✅ Input sanitization and validation
- ✅ Role-based access control
- ✅ Health check endpoint (`/health`)

---

## 📚 Documentation

- **[PHASE1-SETUP.md](PHASE1-SETUP.md)** - Authentication system
- **[PHASE2-COMPLETE.md](PHASE2-COMPLETE.md)** - RPG stats
- **[PHASE3-COMPLETE.md](PHASE3-COMPLETE.md)** - Quests & optimization
- **[PHASE4-COMPLETE.md](PHASE4-COMPLETE.md)** - Combat system
- **[QA-REVIEW.md](QA-REVIEW.md)** - Quality assurance report
- **[QA-IMPLEMENTATION.md](QA-IMPLEMENTATION.md)** - Security hardening
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[LOCAL-SETUP.md](LOCAL-SETUP.md)** - Ollama local development

---

## 🧪 Testing

### API Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### Test User Flow
1. Register new user at http://localhost:8501
2. Login with credentials
3. Select a world
4. Take an action
5. Verify narration response
6. Check stats updated in sidebar

### Test Combat
1. Take multiple actions until combat triggers (~20% chance)
2. Choose attack/magic/defend/flee
3. Verify dice roll animation
4. Check HP updates
5. Win combat and verify XP/gold rewards

---

## 🐛 Troubleshooting

### Backend won't start

**Error**: `SECRET_KEY not set`
```bash
# Generate new key
openssl rand -hex 32

# Update .env
echo "SECRET_KEY=<your-generated-key>" >> .env

# Rebuild
docker-compose up --build
```

### Database errors

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up --build

# Re-seed
docker-compose exec backend python manage.py seed-worlds
docker-compose exec backend python manage.py seed-quests
docker-compose exec backend python manage.py seed-enemies
```

### Port conflicts

```bash
# Check what's using ports
lsof -i :8000  # Backend
lsof -i :8501  # Frontend

# Kill process or change ports in docker-compose.yml
```

### Ollama not working

```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Pull model
ollama pull llama2

# Test generation
ollama run llama2 "Hello"
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **D&D** for inspiring the combat mechanics
- **Streamlit** for the amazing web framework
- **FastAPI** for the blazing-fast backend
- **Ollama** for local LLM support
- **Google Fonts** for medieval typography

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/collabook/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/collabook/discussions)
- **Email**: support@collabook.com

---

## 🗺️ Roadmap

- [ ] Phase 5: Survival mechanics (hunger, sleep, fatigue)
- [ ] Phase 6: Inventory system with items and equipment
- [ ] Phase 7: Multiplayer cooperation (party quests)
- [ ] Phase 8: Achievement system and leaderboards
- [ ] Phase 9: AI-generated character portraits
- [ ] Phase 10: Voice narration (text-to-speech)

---

<div align="center">

**Made with ⚔️ and 🎲 by the Collabook Team**

[⭐ Star us on GitHub](https://github.com/yourusername/collabook) • [🐛 Report Bug](https://github.com/yourusername/collabook/issues) • [💡 Request Feature](https://github.com/yourusername/collabook/issues)

</div>
