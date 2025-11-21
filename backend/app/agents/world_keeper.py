from app.core.llm_client import llm_client

class WorldKeeperAgent:
    """Maintains world consistency and validates actions"""
    
    async def validate_action(self, story_context: dict, user_action: str) -> dict:
        """
        Check if an action is valid within the world rules
        
        Args:
            story_context: World description and rules
            user_action: Proposed action
            
        Returns:
            dict with 'valid' (bool) and 'reason' (str)
        """
        system_prompt = f"""You are a world consistency checker for an interactive story.

World Context:
{story_context.get('world_description', '')}

World Rules/Metadata:
{story_context.get('metadata', {})}

Your task is to determine if a proposed action is consistent with the world rules. 
Respond with ONLY 'VALID' or 'INVALID: <reason>'.
Be permissive - only reject actions that clearly violate established world rules."""

        user_message = f"Proposed action: {user_action}"
        
        response = await llm_client.generate(system_prompt, user_message)
        
        if response.startswith("VALID"):
            return {"valid": True, "reason": "Action is consistent with world rules"}
        else:
            reason = response.replace("INVALID:", "").strip()
            return {"valid": False, "reason": reason}
    
    async def update_world_state(self, current_state: str, new_events: str) -> str:
        """
        Update the story's current state summary based on new events
        
        Args:
            current_state: Previous state summary
            new_events: What just happened
            
        Returns:
            Updated state summary
        """
        system_prompt = """You are a story state tracker. Given the current story state and new events, 
provide an updated summary of the current situation. Keep it concise (2-3 sentences) and focus on 
the most important developments."""

        user_message = f"""Current State: {current_state}

New Events: {new_events}

Provide updated state summary:"""
        
        updated_state = await llm_client.generate(system_prompt, user_message)
        return updated_state

world_keeper_agent = WorldKeeperAgent()
