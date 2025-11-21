from app.core.llm_client import llm_client

class MatchmakerAgent:
    """Matches a new character to an existing story"""
    
    async def find_insertion_point(self, story_context: dict, character: dict) -> str:
        """
        Determine where and how to insert a new character into an ongoing story
        
        Args:
            story_context: World description, current state, active characters
            character: New character profile
        """
        system_prompt = f"""You are a story architect helping integrate new characters into ongoing narratives.

World Context:
{story_context.get('world_description', '')}

Current Story State:
{story_context.get('current_state', 'The story is just beginning...')}

New Character:
- Name: {character.get('name', 'Unknown')}
- Profession: {character.get('profession', 'Adventurer')}
- Description: {character.get('description', '')}

Your task is to suggest a natural and compelling way to introduce this character into the story. Consider:
1. Where they could logically appear given the world rules
2. How they relate to current events
3. What role they might play

Provide a brief (2-3 sentences) insertion point description."""

        user_message = "Suggest how this character should enter the story."
        
        insertion = await llm_client.generate(system_prompt, user_message)
        return insertion

matchmaker_agent = MatchmakerAgent()
