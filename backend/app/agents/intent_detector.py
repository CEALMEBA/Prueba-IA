from typing import Dict, Any
from .base import BaseAgent
import json
import logging

logger = logging.getLogger(__name__)

class IntentDetectorAgent(BaseAgent):
    """Detecta la intención del usuario y redirige al agente correcto"""
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ticket = context.get("ticket", "")
        
        prompt = f"""
        Analiza la siguiente petición y clasifícala en UNA de estas categorías:

        1. "codigo": Si la petición pide generar código, programas, juegos, páginas web, funciones, etc.
        2. "pregunta": Si es una pregunta general, consulta, explicación, o pide información.
        3. "diseño": Si pide ideas de diseño, interfaces, experiencias de usuario, etc.
        4. "datos": Si pide análisis de datos, predicciones, informes, etc.
        5. "otro": Si no encaja en ninguna de las anteriores.

        Petición: {ticket}

        Responde SOLO con la categoría en formato JSON:
        {{"categoria": "codigo", "confianza": 0.95, "explicacion": "breve"}}
        """
        
        messages = [
            {"role": "system", "content": "Eres un clasificador de intenciones. Responde SOLO en JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.3)
            
            # Extraer JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                result = json.loads(response[start:end])
            else:
                result = {"categoria": "codigo", "confianza": 0.5, "explicacion": "Default a código"}
            
            return result
        except Exception as e:
            logger.error(f"Error en IntentDetector: {str(e)}")
            return {"categoria": "codigo", "confianza": 0.5, "explicacion": "Error en detección"}