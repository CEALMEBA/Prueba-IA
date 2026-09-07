from typing import Dict, Any, List
import logging
from datetime import datetime
from ..agents.planner import PlannerAgent
from ..agents.coder import CoderAgent
from ..agents.reviewer import ReviewerAgent

logger = logging.getLogger(__name__)

class AgentPipeline:
    def __init__(self, max_attempts: int = 3):
        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.max_attempts = max_attempts
        self.execution_log = []
        logger.info(f"🚀 Pipeline inicializado con max_attempts={max_attempts}")
        
    def process_ticket(self, ticket: str, history: List[Dict] = None) -> Dict[str, Any]:
        logger.info(f"📝 Procesando: {ticket[:100]}...")
        
        context = {
            "ticket": ticket,
            "history": history or [],
            "max_attempts": self.max_attempts
        }
        
        try:
            # Planner - Descomposición del ticket
            logger.info("📋 Planner: Descomponiendo ticket...")
            plan_result = self.planner.process(context)
            context.update(plan_result)
            self._log_step("Planner", {"tasks": len(plan_result["plan"].get("tasks", []))})
            
            # Loop Coder ↔ Reviewer
            attempt = 1
            while attempt <= self.max_attempts:
                logger.info(f"💻 Coder (Intento {attempt}/{self.max_attempts})")
                context["attempt"] = attempt
                
                code_result = self.coder.process(context)
                context.update(code_result)
                self._log_step(f"Coder_{attempt}", {
                    "code_length": len(code_result.get("code", ""))
                })
                
                logger.info(f"🔍 Reviewer (Intento {attempt}/{self.max_attempts})")
                review_result = self.reviewer.process(context)
                context.update(review_result)
                self._log_step(f"Reviewer_{attempt}", {
                    "approved": review_result.get("approved", False)
                })
                
                if review_result.get("approved", False):
                    logger.info(f"✅ ¡Ticket aprobado en intento {attempt}!")
                    return {
                        "status": "approved",
                        "plan": plan_result["plan"],
                        "code": code_result["code"],
                        "attempts": attempt,
                        "feedback": review_result["feedback"]
                    }
                
                if attempt >= self.max_attempts:
                    logger.warning(f"❌ Máximo de intentos ({attempt}) alcanzado")
                    return {
                        "status": "failed",
                        "plan": plan_result["plan"],
                        "code": code_result["code"],
                        "attempts": attempt,
                        "feedback": review_result["feedback"],
                        "error": "Máximo de intentos alcanzado sin aprobación"
                    }
                
                # Preparar feedback para el siguiente intento
                context["feedback"] = review_result["feedback"]
                attempt += 1
                logger.info(f"🔄 Reintentando con feedback...")
                
        except Exception as e:
            logger.error(f"❌ Error en pipeline: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def _log_step(self, step_name: str, data: Dict[str, Any]):
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "data": data
        })
    
    def get_execution_log(self) -> List[Dict]:
        return self.execution_log