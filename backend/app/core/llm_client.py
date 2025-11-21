import os
import google.generativeai as genai
from typing import Optional

class LLMClient:
    """
    LLM Client supporting Google Gemini (primary) and OpenAI (fallback)
    
    Priority:
    1. Google Gemini (free tier) - if GEMINI_API_KEY is set
    2. OpenAI - if OPENAI_API_KEY is set
    """
    
    def __init__(self):
        self.provider = None
        self.model = None
        
        # Try Google Gemini first (free tier)
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
                        model="gpt-3.5-turbo",  # Cheaper than GPT-4
                        temperature=0.7,
                        api_key=openai_key
                    )
                    self.provider = "openai"
                    print("✓ Using OpenAI GPT-3.5-turbo")
                except Exception as e:
                    print(f"⚠ OpenAI initialization failed: {e}")
        
        if not self.provider:
            raise ValueError("No LLM provider configured. Set GEMINI_API_KEY or OPENAI_API_KEY")
    
    async def generate(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate a response from the LLM"""
        
        if self.provider == "gemini":
            return await self._generate_gemini(system_prompt, user_message, history)
        elif self.provider == "openai":
            return await self._generate_openai(system_prompt, user_message, history)
        else:
            raise ValueError("No LLM provider available")
    
    async def _generate_gemini(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate using Google Gemini"""
        # Combine system prompt with user message for Gemini
        full_prompt = f"{system_prompt}\n\n{user_message}"
        
        # Add conversation history if available
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
        
        # Add conversation history if available
        if history:
            for turn in history:
                messages.append(HumanMessage(content=turn.get("user", "")))
                messages.append(AIMessage(content=turn.get("ai", "")))
        
        messages.append(HumanMessage(content=user_message))
        
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text

llm_client = LLMClient()
