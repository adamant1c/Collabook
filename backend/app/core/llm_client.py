import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
    
    async def generate(self, system_prompt: str, user_message: str, history: list = None) -> str:
        """Generate a response from the LLM"""
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history if available
        if history:
            for turn in history:
                messages.append(HumanMessage(content=turn.get("user", "")))
                messages.append(AIMessage(content=turn.get("ai", "")))
        
        messages.append(HumanMessage(content=user_message))
        
        response = await self.llm.agenerate([messages])
        return response.generations[0][0].text

llm_client = LLMClient()
