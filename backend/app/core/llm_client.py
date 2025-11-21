import os
import google.generativeai as genai
from typing import Optional

class LLMClient:
    """
    LLM Client supporting multiple providers:
    
    Priority:
    1. Ollama (local, 100% FREE) - if OLLAMA_BASE_URL is set
    2. Google Gemini (free tier) - if GEMINI_API_KEY is set
    3. OpenAI - if OPENAI_API_KEY is set
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
                print(f"⚠ Ollama not accessible at {ollama_url}: {e}")
        
        # Try Google Gemini (free tier)
        if not self.provider:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    self.provider = "gemini"
                    print("✓ Using Google Gemini Flash (FREE)")
                except Exception as e:
                    print(f"⚠ Gemini initialization failed: {e}")
        
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
        
        if not self.provider:
            raise ValueError("No LLM provider configured. Set OLLAMA_BASE_URL, GEMINI_API_KEY or OPENAI_API_KEY")
    
    async def generate(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate a response from the LLM"""
        
        if self.provider == "ollama":
            return await self._generate_ollama(system_prompt, user_message, history)
        elif self.provider == "gemini":
            return await self._generate_gemini(system_prompt, user_message, history)
        elif self.provider == "openai":
            return await self._generate_openai(system_prompt, user_message, history)
        else:
            raise ValueError("No LLM provider available")
    
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
        full_prompt = f"{system_prompt}\n\n{user_message}"
        
        if history:
            history_text = "\n\n".join([
                f"User: {turn.get('user', '')}\nAssistant: {turn.get('ai', '')}"
                for turn in history
            ])
            full_prompt = f"{system_prompt}\n\nPrevious conversation:\n{history_text}\n\n{user_message}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating with Gemini: {e}")
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
