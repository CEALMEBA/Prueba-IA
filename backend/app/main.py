from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
from typing import Dict
from datetime import datetime
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from .models.schemas import ChatRequest, ChatResponse
from .orchestrator.pipeline_v2 import AgentPipelineV2  # ← NUEVO

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la ruta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, Dict] = {}
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", 5))

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    file_path_clean = file_path.replace("../", "").replace("..\\", "")
    full_path = FRONTEND_DIR / file_path_clean
    
    if full_path.exists() and full_path.is_file():
        return FileResponse(str(full_path))
    
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions:
            sessions[session_id] = {
                "history": [],
                "pipeline": AgentPipelineV2(max_attempts=MAX_ATTEMPTS)  # ← NUEVO
            }
        
        session = sessions[session_id]
        
        session["history"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        result = session["pipeline"].process_ticket(
            ticket=request.message,
            history=session["history"]
        )
        
        response_message = build_response(result)
        
        session["history"].append({
            "role": "assistant",
            "content": response_message,
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatResponse(
            message=response_message,
            session_id=session_id,
            status=result.get("status", "processing"),
            details=result
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/log")
async def get_session_log(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "log": sessions[session_id]["pipeline"].get_execution_log(),
        "history": sessions[session_id]["history"]
    }

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/sessions")
async def list_sessions():
    return {"sessions": list(sessions.keys())}

def build_response(result: Dict) -> str:
    """Construye la respuesta final para el usuario según el tipo"""
    tipo = result.get("type", "codigo")
    
    if tipo == "codigo":
        if result.get("status") == "approved" or result.get("status") == "approved_forced":
            return (
                "✅ **Código Generado**\n\n"
                "**Resumen del Plan:**\n"
                f"{result['plan'].get('summary', 'Plan implementado')}\n\n"
                "**Código:**\n"
                "```python\n"
                f"{result.get('code', 'No se generó código')}\n"
                "```\n\n"
                f"*Generado en {result.get('attempts', 1)} intento(s)*\n"
            )
        else:
            return f"❌ No se pudo generar el código. {result.get('error', '')}"
    
    elif tipo == "chat":
        return f"💬 {result.get('response', 'No se pudo procesar la pregunta')}"
    
    elif tipo == "diseño":
        design = result.get('design', {})
        return (
            "🎨 **Recomendaciones de Diseño**\n\n"
            f"**Visual:** {design.get('visual', '')}\n\n"
            f"**UX:** {design.get('ux', '')}\n\n"
            f"**UI:** {design.get('ui', '')}\n\n"
            "**Principios:**\n" + "\n".join([f"- {p}" for p in design.get('principios', [])]) + "\n\n"
            "**Recomendaciones:**\n" + "\n".join([f"- {r}" for r in design.get('recomendaciones', [])])
        )
    
    else:
        return f"⚠️ No se pudo procesar la petición. {result.get('error', '')}"