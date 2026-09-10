from typing import Dict, Any
from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ChatAgent(BaseAgent):
    """Responde preguntas generales, explicaciones y consultas"""
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ticket = context.get("ticket", "")
        history = context.get("history", [])
        
        # Extraer historial reciente
        history_context = ""
        if history and len(history) > 0:
            recent = history[-3:] if len(history) > 3 else history
            for msg in recent:
                if isinstance(msg, dict):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    if len(content) > 200:
                        content = content[:200] + "..."
                    history_context += f"{role}: {content}\n"
        
        prompt = f"""
        Responde a la siguiente consulta del usuario:

        {ticket}

        Contexto de la conversación:
        {history_context}

        Instrucciones:
        - Responde de forma clara, concisa y útil
        - Si es una pregunta técnica, da ejemplos concretos
        - Si es una pregunta general, da una respuesta completa
        - Mantén un tono profesional pero amigable
        """
        
        messages = [
            {"role": "system", "content": "Eres un asistente experto y útil. Responde preguntas de cualquier tema."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.7)
            return {
                "response": response,
                "type": "chat"
            }
        except Exception as e:
            logger.error(f"Error en ChatAgent: {str(e)}")
            return {"response": f"Error al procesar: {str(e)}", "type": "error"}