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
from .orchestrator.pipeline import AgentPipeline

# Cargar variables de entorno desde .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la ruta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, Dict] = {}
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", 3))

# Servir archivos estáticos de frontend
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
async def root():
    """Servir el frontend"""
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """Servir archivos estáticos del frontend"""
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
                "pipeline": AgentPipeline(max_attempts=MAX_ATTEMPTS)
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
    
    log_data = sessions[session_id]["pipeline"].get_execution_log()
    history = sessions[session_id]["history"]
    
    # Asegurar que devuelve JSON válido
    return {
        "log": log_data,
        "history": history
    }

def build_response(result: Dict) -> str:
    if result.get("status") == "approved":
        return (
            "✅ **Ticket Aprobado**\n\n"
            "**Resumen del Plan:**\n"
            f"{result['plan'].get('summary', 'Plan implementado')}\n\n"
            "**Código Implementado:**\n"
            "```python\n"
            f"{result.get('code', 'No se generó código')}\n"
            "```\n\n"
            "**Feedback del Revisor:**\n"
            f"{result.get('feedback', 'Sin feedback')}\n\n"
            f"*Aprobado en {result.get('attempts', 1)} intento(s)*\n"
        )
    elif result.get("status") == "failed":
        return (
            "❌ **No se pudo completar**\n\n"
            "**Resumen del Plan:**\n"
            f"{result['plan'].get('summary', 'Plan implementado')}\n\n"
            "**Código:**\n"
            "```python\n"
            f"{result.get('code', 'No se generó')}\n"
            "```\n\n"
            "**Feedback:**\n"
            f"{result.get('feedback', 'Sin feedback')}\n\n"
            f"*Máximo de {result.get('attempts', MAX_ATTEMPTS)} intentos*\n"
            "💡 Puedes pedir cambios específicos.\n"
        )
    else:
        return f"⚠️ Estado desconocido: {result}"