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
        max_attempts = context.get("max_attempts", 5)
        
        prompt = self._build_prompt(plan, code, attempt, max_attempts)
        
        messages = [
            {
                "role": "system", 
                "content": "Eres un revisor de código JUSTO y EQUILIBRADO. APRUEBA el código si es funcional y cumple con la mayoría de los requisitos. No seas demasiado estricto en los primeros intentos. Si el código se puede ejecutar y hace lo principal, APRUÉBALO."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.5)
            
            # Determinar aprobación
            response_upper = response.upper()
            approved = "APROBADO" in response_upper or "APPROVED" in response_upper
            
            # Si es el último intento, aprobar automáticamente
            if attempt >= max_attempts:
                approved = True
                logger.info(f"⚠️ Último intento ({attempt}/{max_attempts}) - Aprobando automáticamente")
            
            return {
                "approved": approved,
                "feedback": response,
                "attempt": attempt,
                "max_attempts_reached": attempt >= max_attempts
            }
        except Exception as e:
            logger.error(f"Error en Reviewer: {str(e)}")
            raise
    
    def _build_prompt(self, plan: dict, code: str, attempt: int, max_attempts: int) -> str:
        """Construye el prompt para el revisor - VERSIÓN MÁS FLEXIBLE"""
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
            "INSTRUCCIONES DE EVALUACIÓN:\n"
            "1. APRUEBA si el código cumple con al menos el 60% de los requisitos\n"
            "2. APRUEBA si el código es funcional y se puede ejecutar\n"
            "3. APRUEBA si tiene los elementos principales del juego\n"
            "4. RECHAZA solo si el código está incompleto o tiene errores graves\n\n"
            "IMPORTANTE:\n"
            "- Si el código tiene canvas y muestra algo → es un buen comienzo\n"
            "- Si el pájaro se mueve o responde a clicks → es funcional\n"
            "- Los detalles menores se pueden mejorar después\n\n"
            "Responde comenzando con APROBADO o RECHAZADO.\n"
            "Si es RECHAZADO, explica qué falta específicamente.\n\n"
            "Tu respuesta:\n"
        )
        
        return prompt