from typing import Dict, Any
from .base import BaseAgent
import json
import logging

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    """Evalúa el código contra el plan y decide si aprueba o no"""
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        plan = context.get("plan", {})
        code = context.get("code", "")
        attempt = context.get("attempt", 1)
        max_attempts = context.get("max_attempts", 3)
        
        prompt = self._build_prompt(plan, code, attempt, max_attempts)
        
        messages = [
            {
                "role": "system", 
                "content": "Eres un revisor de código exigente y justo. Evalúa si el código cumple con el plan y sugiere mejoras concretas. Sé específico en tu feedback y explica claramente por qué apruebas o rechazas. Responde comenzando con APROBADO o RECHAZADO."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.5)
            
            # Determinar aprobación (buscando palabras clave)
            response_upper = response.upper()
            approved = "APROBADO" in response_upper or "APPROVED" in response_upper
            
            # Determinar si se alcanzó el máximo de intentos
            max_reached = attempt >= max_attempts
            
            return {
                "approved": approved,
                "feedback": response,
                "attempt": attempt,
                "max_attempts_reached": max_reached
            }
        except Exception as e:
            logger.error(f"Error en Reviewer: {str(e)}")
            raise
    
    def _build_prompt(self, plan: dict, code: str, attempt: int, max_attempts: int) -> str:
        """Construye el prompt para el revisor usando concatenación"""
        plan_str = json.dumps(plan, indent=2)
        code_preview = code[:3000] if code else 'No se generó código'
        
        # Usar concatenación de strings en lugar de triple comilla
        prompt = (
            "Revisa el siguiente código contra el plan establecido:\n\n"
            "PLAN ORIGINAL:\n"
            f"{plan_str}\n\n"
            "CÓDIGO IMPLEMENTADO:\n"
            "```\n"
            f"{code_preview}\n"
            "```\n\n"
            f"INTENTO: {attempt} de {max_attempts}\n\n"
            "Evalúa el código considerando:\n"
            "1. ¿Cumple con TODAS las tareas del plan?\n"
            "2. ¿Es funcional y lógicamente correcto?\n"
            "3. ¿Tiene manejo de errores adecuado?\n"
            "4. ¿Sigue buenas prácticas de programación?\n"
            "5. ¿El código está bien estructurado y documentado?\n\n"
            "IMPORTANTE:\n"
            "- Responde comenzando con APROBADO o RECHAZADO\n"
            "- Si es RECHAZADO, explica específicamente qué falta o qué está mal\n"
            "- Proporciona sugerencias concretas de mejora\n"
            "- Sé justo pero exigente\n\n"
            "Tu respuesta:\n"
        )
        
        return prompt