from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, model: str = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        # Soporte para OpenRouter y OpenAI
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model or os.getenv("MODEL_NAME", "qwen/qwen3-coder:free")
        logger.info(f"✅ Agente inicializado con modelo: {self.model}")
        
    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def _call_llm(self, messages: list, temperature: float = 0.7) -> str:
        try:
            logger.info(f"📡 Llamando a {self.model} con {len(messages)} mensajes")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Error en LLM: {str(e)}")
            raise