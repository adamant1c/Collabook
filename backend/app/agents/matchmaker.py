from app.core.llm_client import LLMClient

class MatchmakerAgent:
    """Matches a new character to an existing story"""
    
    async def find_insertion_point(self, story_context: dict, character: dict, llm_client: LLMClient, language: str = "en") -> str:
        """
        Determine where and how to insert a new character into an ongoing story
        
        Args:
            story_context: World description, current state, active characters
            character: New character profile
            llm_client: Injected LLM client
            language: Language for the response ("en" or "it")
        """
        # Prompt templates
        templates = {
            "en": {
                "system": """You are a story architect helping integrate new characters into ongoing narratives. Respond in English.

World Context:
{world_description}

Starting Location Context:
{starting_location}

Current Story State:
{current_state}

New Character:
- Name: {name}
- Profession: {profession}
- Description: {description}

Your task is to suggest a natural and compelling way to introduce this character into the story.
Provide a brief (2-3 sentences) insertion point description.
Do NOT use conversational filler like "Here is a suggestion" or "Insertion Point:".
Just provide the narrative description of the character entering the scene.""",
                "user": "Suggest how this character should enter the story."
            },
            "it": {
                "system": """Sei un narratore italiano. IMPORTANTE: Devi scrivere SOLO in ITALIANO.

⚠️ ATTENZIONE - REGOLE OBBLIGATORIE:
- Scrivi ESCLUSIVAMENTE in italiano
- È VIETATO usare parole inglesi
- NON scrivere "Here's", "Insertion Point", "Entry Suggestion", "Potential Role" o QUALSIASI frase inglese
- Scrivi la narrazione DIRETTAMENTE senza etichette o introduzioni

Mondo: {world_description}

Luogo di Partenza: 
{starting_location}

Situazione: {current_state}

Nuovo Personaggio:
- Nome: {name}
- Professione: {profession}  
- Storia: {description}

Scrivi 2-3 frasi che descrivono come {name} entra nella scena. Scrivi SOLO la narrazione in italiano puro, senza titoli o sezioni.""",
                "user": "IMPORTANTE: Rispondi SOLO in lingua italiana. Descrivi come {name} entra nella scena."
            }
        }
        
        # Select template based on language (default to English)
        lang_key = "it" if language.lower().startswith("it") else "en"
        tmpl = templates[lang_key]
        
        # Build starting location string
        starting_loc = ""
        if "starting_location" in story_context:
            sl = story_context["starting_location"]
            if lang_key == "it":
                name = sl.get("name_it") or sl.get("name")
                desc = sl.get("description_it") or sl.get("description")
            else:
                name = sl.get("name")
                desc = sl.get("description")
            
            starting_loc = f"- Nome: {name}\n" if lang_key == "it" else f"- Name: {name}\n"
            if desc:
                starting_loc += f"- Descrizione: {desc}\n" if lang_key == "it" else f"- Description: {desc}\n"
        if not starting_loc:
            starting_loc = "Nessun luogo definito" if lang_key == "it" else "Unknown"

        # Format system prompt
        system_prompt = tmpl["system"].format(
            world_description=story_context.get('world_description', ''),
            starting_location=starting_loc,
            current_state=story_context.get('current_state', 'The story is just beginning...'),
            name=character.get('name', 'Unknown'),
            profession=character.get('profession', 'Adventurer'),
            description=character.get('description', '')
        )

        user_message = tmpl["user"].format(name=character.get('name', 'Unknown'))
        
        insertion = await llm_client.generate(system_prompt, user_message)
        return insertion

matchmaker_agent = MatchmakerAgent()
