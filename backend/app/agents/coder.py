from typing import Dict, Any
from .base import BaseAgent
import json
import logging
import re

logger = logging.getLogger(__name__)

class CoderAgent(BaseAgent):
    """Implementa las tareas en código"""
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        plan = context.get("plan", {})
        feedback = context.get("feedback", None)
        attempt = context.get("attempt", 1)
        
        prompt = self._build_prompt(plan, feedback, attempt)
        
        messages = [
            {
                "role": "system", 
                "content": """Eres un desarrollador senior experto. 
Genera código funcional siguiendo las mejores prácticas.
Incluye comentarios explicativos y manejo de errores.
El código debe ser completo y estar listo para producción.

IMPORTANTE: 
- Si es HTML, DEBE ser un archivo COMPLETO con <!DOCTYPE html>, <html>, <head>, <body>
- Si es Python, debe ser código ejecutable
- Si es JavaScript, debe ser código funcional
- NO incluyas explicaciones fuera del código, SOLO el código en bloques markdown
- El código debe ser AUTO-CONTENIDO y no depender de recursos externos"""
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.3)
            
            # Extraer código
            code = self._extract_code(response)
            
            # Si no hay código, usar la respuesta completa
            if not code:
                code = response
            
            # Detectar el lenguaje
            language = self._detect_language(code)
            
            return {
                "code": code,
                "language": language,
                "explanation": response,
                "attempt": attempt
            }
        except Exception as e:
            logger.error(f"Error en Coder: {str(e)}")
            raise
    
    def _build_prompt(self, plan: dict, feedback: str = None, attempt: int = 1) -> str:
        plan_str = json.dumps(plan, indent=2)
        
        prompt = (
            "Implementa el siguiente plan en código funcional:\n\n"
            f"Plan: {plan_str}\n\n"
            "Requisitos:\n"
            "- Código funcional con todas las tareas implementadas\n"
            "- Comentarios explicativos\n"
            "- Manejo de errores adecuado\n"
            "- Buenas prácticas de programación\n"
            "- Si es HTML, debe ser un archivo COMPLETO con DOCTYPE\n"
            "- El código debe ser AUTO-CONTENIDO\n\n"
            "RESPONDE SOLO CON EL CÓDIGO EN BLOQUES DE CÓDIGO MARKDOWN.\n"
            "NO incluyas explicaciones fuera de los bloques de código."
        )
        
        if feedback:
            prompt += (
                f"\n\n⚠️ FEEDBACK DEL REVISOR (Intento {attempt}):\n"
                f"{feedback}\n\n"
                "IMPORTANTE: Corrige el código basándote en este feedback.\n"
            )
        
        return prompt
    
    def _extract_code(self, response: str) -> str:
        """Extrae el código de la respuesta"""
        # Buscar bloques de código con o sin lenguaje especificado
        code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', response, re.DOTALL)
        
        if code_blocks:
            # Unir todos los bloques de código
            return "\n\n".join(code_blocks)
        
        # Si no hay bloques, devolver la respuesta completa
        return response
    
    def _detect_language(self, code: str) -> str:
        """Detecta el lenguaje del código"""
        if re.search(r'<!DOCTYPE\s+html|<html|<body|<div|<canvas', code, re.IGNORECASE):
            return 'html'
        if re.search(r'def\s+\w+|class\s+\w+:|import\s+\w+|print\(', code):
            return 'python'
        if re.search(r'function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=|=>', code):
            return 'javascript'
        if re.search(r'SELECT|INSERT|UPDATE|CREATE\s+TABLE', code, re.IGNORECASE):
            return 'sql'
        if re.search(r'^{.*}$', code, re.DOTALL):
            return 'json'
        return 'text'