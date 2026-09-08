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
                "content": "Eres un desarrollador senior experto en juegos HTML5 con canvas. Genera código FUNCIONAL y COMPLETO en un solo archivo HTML. El juego debe ser JUGABLE inmediatamente. REGLAS: Usa canvas con requestAnimationFrame. Eventos: click y keydown (ESPACIO). Game Over con reinicio (ESPACIO). El código debe ser AUTO-CONTENIDO."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.3)
            
            # Extraer código
            code = self._extract_code(response)
            
            if not code:
                code = response
            
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
            "Genera código HTML COMPLETO y FUNCIONAL según este plan:\n\n"
            f"PLAN:\n{plan_str}\n\n"
            "REQUISITOS OBLIGATORIOS:\n"
            "- Archivo HTML ÚNICO con <!DOCTYPE html>\n"
            "- CSS en <style> dentro del <head>\n"
            "- JavaScript en <script> al final del <body>\n"
            "- Usa <canvas> con requestAnimationFrame\n"
            "- Eventos: click y keydown (ESPACIO)\n"
            "- Game Over con reinicio (ESPACIO)\n\n"
            "SI ES UN JUEGO DEBE TENER:\n"
            "- Gráficos en canvas\n"
            "- Interacción (click/teclado)\n"
            "- Puntuación\n"
            "- Game Over con reinicio\n"
        )
        
        if feedback:
            prompt += (
                f"\n\nFEEDBACK DEL REVISOR (Intento {attempt}):\n"
                f"{feedback}\n\n"
                "IMPORTANTE: Corrige el código basándote en este feedback.\n"
                "Asegúrate de que el código sea COMPLETO y FUNCIONAL.\n"
            )
        
        prompt += (
            "\nResponde SOLO con el código completo en un bloque de código markdown.\n"
            "NO incluyas explicaciones.\n"
        )
        
        return prompt
    
    def _extract_code(self, response: str) -> str:
        code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', response, re.DOTALL)
        if code_blocks:
            return "\n\n".join(code_blocks)
        return response
    
    def _detect_language(self, code: str) -> str:
        if re.search(r'<!DOCTYPE\s+html|<html', code, re.IGNORECASE):
            return 'html'
        if re.search(r'def\s+\w+|class\s+\w+:|import\s+\w+', code):
            return 'python'
        if re.search(r'function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=', code):
            return 'javascript'
        return 'html'