from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.db_models import MapNode, MapEdge, Character, Story
from app.models.schemas import MapResponse, MapNodeResponse, MapEdgeResponse, MapCharacterPosition, MoveRequest

router = APIRouter(prefix="/map", tags=["map"])

@router.get("/{story_id}", response_model=MapResponse)
async def get_world_map(
    story_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get the full map (nodes and edges) for a specific story/world"""
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Fetch nodes
    nodes = db.query(MapNode).filter(MapNode.story_id == story_id).all()
    
    # Fetch edges
    edges = db.query(MapEdge).filter(MapEdge.story_id == story_id).all()
    
    # Fetch character positions in this story
    characters = db.query(Character).filter(
        Character.story_id == story_id,
        Character.current_location_id.isnot(None)
    ).all()
    
    char_positions = [
        MapCharacterPosition(
            character_id=c.id,
            name=c.user.name or c.user.username,
            location_id=c.current_location_id,
            location_name=c.current_location.name
        ) for c in characters
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "characters": char_positions
    }

@router.post("/move", response_model=MapCharacterPosition)
async def move_character(
    request: MoveRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Move a character to a new location"""
    character = db.query(Character).filter(Character.id == request.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Check if already at target location
    if character.current_location_id == request.target_node_id:
        return MapCharacterPosition(
            character_id=character.id,
            name=character.user.name or character.user.username,
            location_id=character.current_location_id,
            location_name=db.query(MapNode).filter(MapNode.id == character.current_location_id).first().name
        )
    
    # Verify ownership (or admin)
    if character.user.username != current_user.username and current_user.username != "admin": # Simple check, refine if needed
         raise HTTPException(status_code=403, detail="Not authorized to move this character")

    # Verify target node exists in the same story
    target_node = db.query(MapNode).filter(
        MapNode.id == request.target_node_id,
        MapNode.story_id == character.story_id
    ).first()
    if not target_node:
        raise HTTPException(status_code=404, detail="Target location not found in this world")

    # Check if movement is valid (connected nodes)
    if character.current_location_id:
        edge = db.query(MapEdge).filter(
            ((MapEdge.from_node_id == character.current_location_id) & (MapEdge.to_node_id == request.target_node_id)) |
            (MapEdge.bidirectional & (MapEdge.from_node_id == request.target_node_id) & (MapEdge.to_node_id == character.current_location_id))
        ).first()
        
        if not edge:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Locations are not connected")

    # Update position
    character.current_location_id = request.target_node_id
    db.commit()
    db.refresh(character)

    return MapCharacterPosition(
        character_id=character.id,
        name=character.user.name or character.user.username,
        location_id=character.current_location_id,
        location_name=target_node.name
    )
