"""
Items and Inventory API

Endpoints for managing character inventory and using consumable items.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.db_models import User, Character, Item, Inventory, ItemType
from app.models.schemas import ItemCreate, ItemResponse, InventoryResponse, UseItemRequest, RestRequest
from app.core.survival import consume_item, rest_action
from typing import List

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/inventory/{character_id}", response_model=List[InventoryResponse])
async def get_inventory(
    character_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get character's inventory"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")
    
    inventory = db.query(Inventory).filter(
        Inventory.character_id == character_id
    ).all()
    
    return inventory

@router.post("/use")
async def use_item(
    character_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Consume an item from inventory"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Find item in inventory
    inv_item = db.query(Inventory).filter(
        Inventory.character_id == character_id,
        Inventory.item_id == item_id
    ).first()
    
    if not inv_item or inv_item.quantity <= 0:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    
    item = inv_item.item
    
    # Use item
    result = consume_item(character, item, db)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Decrease quantity
    inv_item.quantity -= 1
    if inv_item.quantity <= 0:
        db.delete(inv_item)
    
    db.commit()
    
    return {
        **result,
        "character": {
            "hunger": character.hunger,
            "thirst": character.thirst,
            "fatigue": character.fatigue,
            "hp": character.user.hp
        }
    }

@router.post("/rest")
async def take_rest(
    character_id: str,
    hours: int = 8,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Character rests to reduce fatigue"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if hours < 1 or hours > 24:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 24")
    
    result = rest_action(character, hours)
    db.commit()
    
    return {
        **result,
        "character": {
            "hunger": character.hunger,
            "thirst": character.thirst,
            "fatigue": character.fatigue
        }
    }

@router.get("/available", response_model=List[ItemResponse])
async def list_available_items(
    item_type: ItemType = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available items (for shop/reference)"""
    query = db.query(Item)
    
    if item_type:
        query = query.filter(Item.item_type == item_type)
    
    items = query.all()
    return items

@router.post("/give/{character_id}/{item_id}")
async def give_item_to_character(
    character_id: str,
    item_id: str,
    quantity: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Give an item to character (admin only or for rewards)
    
    Can be called by:
    - Admins (to give items to anyone)
    - System (for loot rewards)
    - Player (for their own character, e.g., buying from shop)
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Check permissions
    if character.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if character already has this item
    existing = db.query(Inventory).filter(
        Inventory.character_id == character_id,
        Inventory.item_id == item_id
    ).first()
    
    if existing:
        # Increase quantity
        existing.quantity += quantity
    else:
        # Create new inventory entry
        new_inv = Inventory(
            character_id=character_id,
            item_id=item_id,
            quantity=quantity
        )
        db.add(new_inv)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Added {quantity}x {item.name} to inventory"
    }

@router.post("/create", response_model=ItemResponse)
async def create_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new item (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    new_item = Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item
