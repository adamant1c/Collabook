from app.core.llm_client import llm_client

class NarratorAgent:
    """Generates story narration based on user actions"""
    
    async def generate_narration(self, story_context: dict, character: dict, user_action: str, history: list) -> str:
        """
        Generate the next part of the story based on user action
        
        Args:
            story_context: World description, current state, genre
            character: Character info (name, profession, description)
            user_action: What the user chose to do
            history: Previous turns in the story
        """
        system_prompt = f"""You are a creative storyteller narrating an interactive story.

World Context:
{story_context.get('world_description', '')}

Genre: {story_context.get('genre', 'Fantasy')}

Current Story State:
{story_context.get('current_state', 'The story is just beginning...')}

Character:
- Name: {character.get('name', 'Unknown')}
- Profession: {character.get('profession', 'Adventurer')}
- Description: {character.get('description', '')}

Your task is to narrate what happens next based on the character's action. Keep the narration engaging, vivid, and consistent with the world. Leave room for the character to make the next choice. Write 2-4 paragraphs."""

        user_message = f"The character decides to: {user_action}"
        
        narration = await llm_client.generate(system_prompt, user_message, history)
        return narration

narrator_agent = NarratorAgent()
