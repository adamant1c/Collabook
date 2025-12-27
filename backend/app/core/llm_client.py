import os
from google import genai
from google.genai.types import GenerateContentConfig
from typing import Optional
import asyncio

class MockLLMClient:
    """
    Mock LLM Client for testing or when no provider is configured.
    Returns canned responses to allow the application to function.
    """
    def __init__(self):
        print("⚠ Using Mock LLM Client (No valid API keys found)")
        
    async def generate(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate a mock response"""
        await asyncio.sleep(1) # Simulate latency
        
        # Simple keyword matching for context
        if "character" in user_message.lower() or "profile" in user_message.lower():
            return "As you step into this world, you feel a surge of potential. Your character stands ready for adventure, their destiny yet to be written."
        elif "attack" in user_message.lower() or "fight" in user_message.lower():
            return "You lunge forward with determination! The enemy attempts to dodge, but your strike finds its mark. The clash of steel rings out."
        elif "look" in user_message.lower() or "examine" in user_message.lower():
            return "You observe your surroundings carefully. The details of the world stand out—the texture of the stone, the play of light and shadow, the distant sounds of life."
        else:
            return f"The Dungeon Master nods at your action: '{user_message}'. The world shifts slightly in response, and you feel the weight of your choices."

class LLMClient:
    """
    LLM Client supporting multiple providers:
    
    Priority:
    1. Ollama (local, 100% FREE) - if OLLAMA_BASE_URL is set
    2. Google Gemini (free tier) - if GEMINI_API_KEY is set
    3. OpenAI - if OPENAI_API_KEY is set
    4. Mock - if no provider is configured
    """
    
    def __init__(self):
        self.provider = None
        self.model = None
        self.ollama_url = None
        self.ollama_model = None
        
        # Try Ollama first (local, completely free)
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        if ollama_url:
            try:
                import requests
                # Test if Ollama is accessible
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    self.ollama_url = ollama_url
                    self.ollama_model = ollama_model
                    self.provider = "ollama"
                    print(f"✓ Using Ollama ({ollama_model}) - 100% FREE & LOCAL")
            except Exception as e:
                print(f"ℹ Ollama not accessible at {ollama_url}: {e}")
        
        # Try Google Gemini (free tier)
        if not self.provider:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                try:

                    self.genai_client = genai.Client(api_key=gemini_key)  # or () if env var GEMINI_API_KEY is set
                    self.provider = "gemini"
                    self.model = type('FakeModel', (), {
                        'generate_content_async': lambda prompt: self.genai_client.aio.models.generate_content(
                            model="models/gemini-2.5-flash",
                            contents=[{"role": "user", "parts": [{"text": prompt}]}]
                        )
                    })()
                    print("✓ Using Google GenAI SDK (new unified)")
                except Exception as e:
                    print(f"⚠ Gemini initialization failed: {e}")

        # Initialize Groq (can be primary or fallback)
        self.groq_client = None
        self.groq_model = "llama-3.3-70b-versatile" # Excellent free model
        groq_key = os.getenv("GROQ_API_KEY")
        
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
                print(f"✓ Groq initialized (Model: {self.groq_model})")
                
                # If no other provider is set, use Groq as primary
                if not self.provider:
                    self.provider = "groq"
                    print("✓ Using Groq as PRIMARY provider")
            except Exception as e:
                print(f"⚠ Groq initialization failed: {e}")
        
        # Fallback to OpenAI
        if not self.provider:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    from langchain_openai import ChatOpenAI
                    self.model = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        temperature=0.7,
                        api_key=openai_key
                    )
                    self.provider = "openai"
                    print("✓ Using OpenAI GPT-3.5-turbo")
                except Exception as e:
                    print(f"⚠ OpenAI initialization failed: {e}")
        
        # Fallback to Mock
        if not self.provider:
            self.model = MockLLMClient()
            self.provider = "mock"
            print("⚠ No LLM provider configured. Using Mock LLM for testing.")
    
    async def generate(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate a response from the LLM with fallback support"""
        
        try:
            if self.provider == "ollama":
                return await self._generate_ollama(system_prompt, user_message, history)
            elif self.provider == "gemini":
                try:
                    return await self._generate_gemini(system_prompt, user_message, history)
                except Exception as e:
                    # If Gemini fails (e.g. quota exceeded) and Groq is available, try Groq
                    if self.groq_client:
                        print(f"⚠️ Gemini failed ({str(e)}). Falling back to Groq...")
                        return await self._generate_groq(system_prompt, user_message, history)
                    raise e # Re-raise if no fallback
            elif self.provider == "groq":
                return await self._generate_groq(system_prompt, user_message, history)
            elif self.provider == "openai":
                return await self._generate_openai(system_prompt, user_message, history)
            elif self.provider == "mock":
                return await self.model.generate(system_prompt, user_message, history)
            else:
                return "Error: No LLM provider available."
        except Exception as e:
            print(f"❌ All LLM providers failed: {e}")
            raise e
    
    async def _generate_ollama(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate using Ollama (local LLM)"""
        import requests
        
        # Build full prompt with history
        full_prompt = f"{system_prompt}\n\n"
        
        if history:
            for turn in history:
                full_prompt += f"User: {turn.get('user', '')}\n"
                full_prompt += f"Assistant: {turn.get('ai', '')}\n\n"
        
        full_prompt += f"{user_message}\n\nAssistant:"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500  # Max tokens for response
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error generating with Ollama: {e}")
            raise

    async def _generate_gemini(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate using Google Gemini"""


        # Manteniamo lo stesso approccio "stringa unica" che avevi prima
        full_prompt = f"{system_prompt}\n\n{user_message}"

        if history:
            history_text = "\n\n".join([
                f"User: {turn.get('user', '')}\nAssistant: {turn.get('ai', '')}"
                for turn in history
            ])
            full_prompt = f"{system_prompt}\n\nPrevious conversation:\n{history_text}\n\n{user_message}"

        try:
            # Add retry logic for ResourceExhausted (429) errors
            from google.genai.types import ResourceExhausted
            import random

            max_retries = 3
            base_delay = 2

            for attempt in range(max_retries):
                try:
                    # Nuova chiamata async con il nuovo client
                    response = await self.genai_client.aio.models.generate_content(
                        model="models/gemini-2.5-flash",  # ← cambia qui se usi un altro modello
                        contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
                        config=GenerateContentConfig(
                            system_instruction=system_prompt,  # ← sposto system prompt qui (più corretto)
                            temperature=0.7
                        )
                    )
                    return response.text

                except ResourceExhausted as e:
                    if attempt == max_retries - 1:
                        print(f"❌ Gemini Quota Exceeded after {max_retries} attempts.")
                        raise e  # Raise to trigger fallback to Groq

                    # Exponential backoff with jitter
                    delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                    print(f"⏳ Gemini Quota Exceeded. Retrying in {delay:.2f}s... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)

        except Exception as e:
            print(f"Error generating with Gemini: {e}")
            raise
            
    async def _generate_groq(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate using Groq API"""
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            for turn in history:
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("ai", "")})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Run sync Groq client in thread pool to not block async loop
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                lambda: self.groq_client.chat.completions.create(
                    messages=messages,
                    model=self.groq_model,
                    temperature=0.7,
                    max_tokens=1024,
                )
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating with Groq: {e}")
            raise

    async def _generate_openai(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate using OpenAI"""
        from langchain.schema import HumanMessage, SystemMessage, AIMessage
        
        messages = [SystemMessage(content=system_prompt)]
        
        if history:
            for turn in history:
                messages.append(HumanMessage(content=turn.get("user", "")))
                messages.append(AIMessage(content=turn.get("ai", "")))
        
        messages.append(HumanMessage(content=user_message))
        
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text

llm_client = LLMClient()
