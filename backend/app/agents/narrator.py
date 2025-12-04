from app.core.llm_client import llm_client

class NarratorAgent:
    """Generates story narration based on user actions"""
    
    async def generate_narration(self, story_context: dict, character: dict, user_action: str, history: list, language: str = "en") -> str:
        """
        Generate the next part of the story based on user action
        
        Args:
            story_context: World description, current state, genre
            character: Character info (name, profession, description)
            user_action: What the user chose to do
            history: Previous turns in the story
            language: Language for the response ("en" or "it")
        """
        # Prompt templates
        templates = {
            "en": {
                "system": """You are a creative storyteller narrating an interactive story.

World Context:
{world_description}

Genre: {genre}

Current Story State:
{current_state}

Character:
- Name: {name}
- Profession: {profession}
- Description: {description}

Your task is to narrate what happens next based on the character's action. Keep the narration engaging, vivid, and consistent with the world. Leave room for the character to make the next choice. Write 2-4 paragraphs.""",
                "user": "The character decides to: {action}"
            },
            "it": {
                "system": """Sei un narratore italiano di storie interattive. IMPORTANTE: Devi scrivere SOLO in ITALIANO.

⚠️ ATTENZIONE - REGOLE OBBLIGATORIE:
- Scrivi ESCLUSIVAMENTE in italiano
- È VIETATO usare parole inglesi
- NON scrivere "Here's", "The", "You", "Your" o QUALSIASI parola inglese
- Scrivi la narrazione DIRETTAMENTE in italiano puro

Mondo:
{world_description}

Genere: {genre}

Situazione:
{current_state}

Personaggio:
- Nome: {name}
- Professione: {profession}
- Storia: {description}

Narra cosa succede dopo l'azione del personaggio. Rendi la narrazione coinvolgente e coerente con il mondo. Lascia spazio per la prossima scelta. Scrivi 2-4 paragrafi in italiano usando "tu" per il personaggio.""",
                "user": "Il personaggio fa: {action}"
            }
        }
        
        # Select template based on language
        lang_key = "it" if language == "it" else "en"
        tmpl = templates[lang_key]
        
        # Format system prompt
        system_prompt = tmpl["system"].format(
            world_description=story_context.get('world_description', ''),
            genre=story_context.get('genre', 'Fantasy'),
            current_state=story_context.get('current_state', 'The story is just beginning...'),
            name=character.get('name', 'Unknown'),
            profession=character.get('profession', 'Adventurer'),
            description=character.get('description', '')
        )

        user_message = tmpl["user"].format(action=user_action)
        
        narration = await llm_client.generate(system_prompt, user_message, history)
        return narration

narrator_agent = NarratorAgent()
