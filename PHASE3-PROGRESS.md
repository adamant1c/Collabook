# Phase 3: Quest System - WORK IN PROGRESS

## ✅ Completed So Far

### Backend (80% Complete)

#### Database Schema ✅
- Quest table with objectives, rewards, quest_givers
- PlayerQuest table for tracking player progress
- QuestType enum (MAIN, SIDE)
- QuestStatus enum (NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED)
- Character.gold field added
- All relationships configured

#### API Endpoints ✅
- `POST /quests/` - Create quest (Admin only)
- `GET /quests/story/{story_id}` - List quests for story
- `POST /quests/{quest_id}/accept` - Accept quest
- `GET /quests/character/{character_id}` - Get character quests
- `POST /quests/{quest_id}/complete` - Complete quest and award rewards

#### Pydantic Schemas ✅
- QuestCreate
- QuestResponse  
- PlayerQuestResponse
- QuestObjective
- Quest completion flow schemas

#### Reward System ✅
- XP rewards using existing award_xp()
- Gold rewards
- Level up on quest completion

---

## ⏳ TODO (20% Remaining)

### 1. Default Quests Seeder
Need to add `seed-quests` command to `manage.py`:
- 3 main quests (one per world)
- 6-9 side quests (2-3 per world)

### 2. Frontend Quest UI
- Quest list in sidebar
- Quest details modal
- Accept/Complete buttons
- Progress tracking display

### 3. LLM Integration (Hybrid Completion)
Update DM prompt to:
- Include active quests in context
- Suggest when objectives completed
- Show "Quest Complete!" hint in narration

---

## 🎮 How It Works (Hybrid Completion - Option C)

1. **Player accepts quest** → Quest added to "Active Quests"
2. **Player takes actions** → LLM narrates with quest context
3. **LLM detects completion** → Adds hint in narration: "✨ *Quest Complete: [Title]*"
4. **Player confirms** → Clicks "Complete Quest" button
5. **Rewards awarded** → XP, gold, levelup animation

---

## 📝 Quest Structure Example

```json
{
  "title": "The King's Tournament",
  "description": "Prove your worth in combat",
  "quest_type": "main",
  "objectives": [
    {"id": "train", "description": "Train with Master-at-Arms"},
    {"id": "qualify", "description": "Win 3 duels"},
    {"id": "champion", "description": "Defeat champion"}
  ],
  "xp_reward": 500,
  "gold_reward": 1000,
  "quest_giver": "King Harold III",
  "required_level": 1
}
```

---

## 🧪 Testing (When Complete)

```bash
# 1. Rebuild
docker-compose down -v
docker-compose up --build

# 2. Seed quests
docker-compose exec backend python manage.py seed-quests

# 3. Test flow
- Register player
- Join world
- See available quests
- Accept quest
- Take actions
- Complete quest
- Receive rewards
```

---

## 📊 Database Changes

**New tables**:
- `quests`
- `player_quests`

**Updated tables**:
- `characters` → added `gold` field
- `stories` → added `quests` relationship
- `characters` → added `player_quests` relationship

**⚠️ Migration**: Fresh database needed (docker-compose down -v)

---

## Next Session TODO:

1. ✅ Complete `seed-quests` command in manage.py
2. ✅ Add frontend quest UI
3. ✅ Integrate LLM quest hints
4. ✅ Test complete flow
5. → Move to Phase 4 (Combat)!

---

*Backend structure ready, frontend next!*
