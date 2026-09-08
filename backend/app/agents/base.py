from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import os
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Clase base para todos los agentes - Configurado para Azure OpenAI"""
    
    def __init__(self, model: str = None):
        # === SOLO LEE VARIABLES DE AZURE ===
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        # Validar que todas las variables estén presentes
        if not api_key:
            raise ValueError("❌ AZURE_OPENAI_API_KEY no está configurada")
        if not endpoint:
            raise ValueError("❌ AZURE_OPENAI_ENDPOINT no está configurada")
        if not deployment:
            raise ValueError("❌ AZURE_OPENAI_DEPLOYMENT no está configurada")
        
        # Limpiar el endpoint (eliminar /chat/completions si existe)
        if "/chat/completions" in endpoint:
            endpoint = endpoint.split("/chat/completions")[0]
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        
        # Crear cliente AzureOpenAI
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.model = deployment
        
        logger.info(f"✅ Agente inicializado con Azure OpenAI")
        logger.info(f"📍 Endpoint: {endpoint}")
        logger.info(f"📦 Deployment: {deployment}")
        logger.info(f"📌 API Version: {api_version}")
        
    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la entrada y retorna el resultado"""
        pass
    
    def _call_llm(self, messages: list, temperature: float = 0.7) -> str:
        """Maneja la llamada a la API con manejo de errores"""
        try:
            logger.info(f"📡 Llamando a Azure OpenAI (deployment: {self.model})")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Error en Azure OpenAI: {str(e)}")
            raise