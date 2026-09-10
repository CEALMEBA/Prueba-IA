from typing import Dict, Any
from .base import BaseAgent
import json
import logging

logger = logging.getLogger(__name__)

class DesignerAgent(BaseAgent):
    """Genera ideas de diseño, interfaces y experiencia de usuario"""
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ticket = context.get("ticket", "")
        
        prompt = f"""
        Genera ideas y recomendaciones de diseño para:

        {ticket}

        Incluye:
        1. Aspectos visuales (colores, tipografía, layout)
        2. Experiencia de usuario (flujo, interacciones)
        3. Elementos de UI (botones, menús, tarjetas)
        4. Principios de diseño aplicados
        5. Recomendaciones para implementación

        Responde en formato JSON:
        {{
            "visual": "descripción",
            "ux": "descripción",
            "ui": "descripción",
            "principios": ["lista"],
            "recomendaciones": ["lista"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "Eres un diseñador experto en UI/UX. Genera recomendaciones de diseño."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(messages, temperature=0.8)
            
            # Extraer JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                result = json.loads(response[start:end])
            else:
                result = {
                    "visual": "No se pudo generar diseño", 
                    "ux": "Error", 
                    "ui": "Error", 
                    "principios": [], 
                    "recomendaciones": []
                }
            
            return result
        except Exception as e:
            logger.error(f"Error en DesignerAgent: {str(e)}")
            return {
                "visual": "Error al generar diseño", 
                "ux": str(e), 
                "ui": "Error", 
                "principios": [], 
                "recomendaciones": ["Reintentar con más detalles"]
            }