from typing import Dict, Any, List
from .base import BaseAgent
import json
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Descompone el ticket en tareas técnicas concretas"""
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ticket = context.get("ticket", "")
        history = context.get("history", [])
        
        prompt = self._build_prompt(ticket, history)
        
        messages = [
            {"role": "system", "content": """Eres un arquitecto de software experto. 
Descompone tickets de features en tareas técnicas claras y accionables. 
Siempre responde en formato JSON válido."""},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.5)
            
            # Intentar parsear JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    plan = json.loads(json_str)
                else:
                    raise ValueError("No se encontró JSON")
            except:
                # Fallback
                plan = {
                    "summary": "Plan generado automáticamente",
                    "tasks": [
                        {"id": 1, "description": response[:200], "dependencies": []}
                    ],
                    "technical_notes": ["Revisar implementación manualmente"]
                }
            
            return {
                "plan": plan,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Error en Planner: {str(e)}")
            raise
    
    def _build_prompt(self, ticket: str, history: List[Dict]) -> str:
        """Construye el prompt con el historial de conversación"""
        history_context = ""
        if history and len(history) > 0:
            recent = history[-3:] if len(history) > 3 else history
            history_context = "\n\nContexto de conversación anterior:\n"
            for msg in recent:
                # Extraer el contenido del mensaje independientemente del formato
                if isinstance(msg, dict):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    # Si el contenido es muy largo, truncarlo
                    if len(content) > 200:
                        content = content[:200] + "..."
                    history_context += f"{role}: {content}\n"
                elif isinstance(msg, str):
                    history_context += f"{msg}\n"
        
        return f"""
        Descompón el siguiente ticket en tareas técnicas específicas:
        
        Ticket: {ticket}
        {history_context}
        
        IMPORTANTE: Responde SOLO en formato JSON con la siguiente estructura:
        {{
            "summary": "resumen ejecutivo del plan (1-2 líneas)",
            "tasks": [
                {{"id": 1, "description": "tarea específica y detallada", "dependencies": []}},
                {{"id": 2, "description": "siguiente tarea", "dependencies": [1]}}
            ],
            "technical_notes": ["nota técnica 1", "nota técnica 2"]
        }}
        
        Asegúrate de que las tareas sean concretas y accionables para un desarrollador.
        """