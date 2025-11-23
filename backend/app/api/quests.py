from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_user, require_admin
from app.core.rpg_stats import award_xp
from app.models.db_models import Quest, PlayerQuest, Character, QuestStatus, QuestType, User
from app.models.schemas import (
    QuestCreate, QuestResponse, QuestAccept, QuestComplete,
    PlayerQuestResponse
)

router = APIRouter(prefix="/quests", tags=["quests"])

@router.post("/", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(
    quest_data: QuestCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new quest (Admin only)"""
    
    # Convert Pydantic objectives to dict
    objectives = [obj.dict() for obj in quest_data.objectives]
    
    quest = Quest(
        story_id=quest_data.story_id,
        title=quest_data.title,
        description=quest_data.description,
        quest_type=QuestType(quest_data.quest_type),
        objectives=objectives,
        xp_reward=quest_data.xp_reward,
        gold_reward=quest_data.gold_reward,
        quest_giver=quest_data.quest_giver,
        quest_giver_description=quest_data.quest_giver_description,
        required_level=quest_data.required_level,
        is_repeatable=quest_data.is_repeatable
    )
    
    db.add(quest)
    db.commit()
    db.refresh(quest)
    
    return quest

@router.get("/story/{story_id}", response_model=List[QuestResponse])
async def list_story_quests(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all quests available in a story"""
    quests = db.query(Quest).filter(Quest.story_id == story_id).all()
    return quests

@router.post("/{quest_id}/accept", status_code=status.HTTP_201_CREATED)
async def accept_quest(
    quest_id: str,
    quest_accept: QuestAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a quest"""
    
    # Verify quest exists
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Verify character exists and belongs to current user
    character = db.query(Character).filter(Character.id == quest_accept.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    # Check level requirement
    if current_user.level < quest.required_level:
        raise HTTPException(
            status_code=400,
            detail=f"Requires level {quest.required_level}"
        )
    
    # Check if already accepted
    existing = db.query(PlayerQuest).filter(
        PlayerQuest.character_id == character.id,
        PlayerQuest.quest_id == quest_id,
        PlayerQuest.status != QuestStatus.COMPLETED
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Quest already accepted")
    
    # Create player quest
    player_quest = PlayerQuest(
        character_id=character.id,
        quest_id=quest_id,
        status=QuestStatus.IN_PROGRESS
    )
    
    db.add(player_quest)
    db.commit()
    db.refresh(player_quest)
    
    return {"message": "Quest accepted!", "player_quest_id": player_quest.id}

@router.get("/character/{character_id}", response_model=List[PlayerQuestResponse])
async def get_character_quests(
    character_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all quests for a character"""
    
    # Verify character belongs to user
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    player_quests = db.query(PlayerQuest).filter(
        PlayerQuest.character_id == character_id
    ).all()
    
    return player_quests

@router.post("/{quest_id}/complete")
async def complete_quest(
    quest_id: str,
    quest_complete: QuestComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark quest as complete and award rewards (Player confirms after LLM suggests)"""
    
    # Find player quest
    player_quest = db.query(PlayerQuest).filter(
        PlayerQuest.quest_id == quest_id,
        PlayerQuest.character_id == quest_complete.character_id
    ).first()
    
    if not player_quest:
        raise HTTPException(status_code=404, detail="Quest not accepted")
    
    if player_quest.status == QuestStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Quest already completed")
    
    # Verify character belongs to user
    if player_quest.character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    quest = player_quest.quest
    
    # Mark as complete
    player_quest.status = QuestStatus.COMPLETED
    player_quest.completed_at = datetime.utcnow()
    
    # Award rewards
    user = current_user
    
    # Award XP
    level_up_info = award_xp(user, quest.xp_reward)
    
    # Award gold
    player_quest.character.gold += quest.gold_reward
    
    db.commit()
    
    return {
        "message": "Quest completed!",
        "xp_gained": quest.xp_reward,
        "gold_gained": quest.gold_reward,
        "level_up": level_up_info if level_up_info else None
    }
