from typing import Dict, Any, List
import logging
from datetime import datetime
from ..agents.intent_detector import IntentDetectorAgent
from ..agents.planner import PlannerAgent
from ..agents.coder import CoderAgent
from ..agents.reviewer import ReviewerAgent
from ..agents.chat import ChatAgent
from ..agents.designer import DesignerAgent

logger = logging.getLogger(__name__)

class AgentPipelineV2:
    """Orquestador versátil - Maneja cualquier tipo de petición"""
    
    def __init__(self, max_attempts: int = 5):
        self.intent_detector = IntentDetectorAgent()
        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.chat = ChatAgent()
        self.designer = DesignerAgent()
        self.max_attempts = max_attempts
        self.execution_log = []
        logger.info(f"🚀 Pipeline V2 inicializado con max_attempts={max_attempts}")
    
    def process_ticket(self, ticket: str, history: List[Dict] = None) -> Dict[str, Any]:
        logger.info(f"📝 Procesando: {ticket[:100]}...")
        
        # PASO 1: Detectar intención
        context = {
            "ticket": ticket,
            "history": history or [],
            "max_attempts": self.max_attempts
        }
        
        try:
            intent_result = self.intent_detector.process(context)
            categoria = intent_result.get("categoria", "codigo")
            confianza = intent_result.get("confianza", 0.5)
            
            logger.info(f"🎯 Intención detectada: {categoria} (confianza: {confianza:.2f})")
            self._log_step("IntentDetector", intent_result)
            
            # PASO 2: Redirigir según la categoría
            if categoria == "codigo":
                return self._handle_code(ticket, history, context)
            
            elif categoria == "pregunta":
                return self._handle_chat(ticket, history, context)
            
            elif categoria == "diseño":
                return self._handle_design(ticket, history, context)
            
            elif categoria == "datos":
                # Por ahora lo manejamos como chat
                return self._handle_chat(ticket, history, context)
            
            else:
                # Default: chat
                return self._handle_chat(ticket, history, context)
                
        except Exception as e:
            logger.error(f"❌ Error en pipeline: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def _handle_code(self, ticket: str, history: List[Dict], context: Dict) -> Dict[str, Any]:
        """Maneja peticiones de código (el flujo original)"""
        logger.info("💻 Generando código...")
        self._log_step("Orquestador", {"accion": "generar_codigo"})
        
        # Planner
        plan_result = self.planner.process(context)
        context.update(plan_result)
        self._log_step("Planner", {"tasks": len(plan_result["plan"].get("tasks", []))})
        
        # Loop Coder ↔ Reviewer
        attempt = 1
        while attempt <= self.max_attempts:
            context["attempt"] = attempt
            
            # Coder
            code_result = self.coder.process(context)
            context.update(code_result)
            self._log_step(f"Coder_{attempt}", {"code_length": len(code_result.get("code", ""))})
            
            # Reviewer
            review_result = self.reviewer.process(context)
            context.update(review_result)
            self._log_step(f"Reviewer_{attempt}", {"approved": review_result.get("approved", False)})
            
            if review_result.get("approved", False):
                return {
                    "status": "approved",
                    "type": "codigo",
                    "plan": plan_result["plan"],
                    "code": code_result["code"],
                    "attempts": attempt,
                    "feedback": review_result["feedback"]
                }
            
            if attempt >= self.max_attempts:
                return {
                    "status": "approved_forced",
                    "type": "codigo",
                    "plan": plan_result["plan"],
                    "code": code_result["code"],
                    "attempts": attempt,
                    "feedback": review_result["feedback"],
                    "forced": True
                }
            
            context["feedback"] = review_result["feedback"]
            attempt += 1
        
        return {"status": "failed", "type": "codigo", "error": "No se pudo generar código"}
    
    def _handle_chat(self, ticket: str, history: List[Dict], context: Dict) -> Dict[str, Any]:
        """Maneja preguntas generales"""
        logger.info("💬 Respondiendo pregunta...")
        self._log_step("Orquestador", {"accion": "responder_pregunta"})
        
        result = self.chat.process(context)
        return {
            "status": "success",
            "type": "chat",
            "response": result.get("response", ""),
            "feedback": "Pregunta respondida"
        }
    
    def _handle_design(self, ticket: str, history: List[Dict], context: Dict) -> Dict[str, Any]:
        """Maneja peticiones de diseño"""
        logger.info("🎨 Generando diseño...")
        self._log_step("Orquestador", {"accion": "generar_diseno"})
        
        result = self.designer.process(context)
        return {
            "status": "success",
            "type": "diseño",
            "design": result,
            "feedback": "Diseño generado"
        }
    
    def _log_step(self, step_name: str, data: Dict[str, Any]):
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "data": data
        })
    
    def get_execution_log(self) -> List[Dict]:
        return self.execution_log