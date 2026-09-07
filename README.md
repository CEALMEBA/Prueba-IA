# AI Agents Pipeline - Sistema Multi-Agente


🤖 AI Agents Pipeline - Sistema Multi-Agente
📋 Visión General
AI Agents Pipeline es un sistema multi-agente que convierte tickets de features en código funcional mediante la colaboración de tres agentes de IA especializados. El usuario escribe un ticket en lenguaje natural y el sistema lo descompone en tareas técnicas, genera código y lo revisa automáticamente, todo en un loop de mejora continua.
Demo en vivo: https://ai-agents-pipeline.onrender.com
________________________________________
Arquitectura del Sistema
text
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO                                 │
│                    (Chat Interactivo)                           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (HTML/CSS/JS)                     │
│                  Interfaz de chat multi-turno                   │
│              Muestra logs en tiempo real y código               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI API)                         │
│              Endpoints: /api/chat, /api/session/{id}/log        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORQUESTADOR (AgentPipeline)                   │
│                   Coordina la ejecución de agentes              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   PLANNER     │   │    CODER      │   │   REVIEWER    │
│  Descompone   │──▶│  Implementa   │──▶│   Evalúa y    │
│  el ticket    │   │  el código    │   │   aprueba     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  LOOP DE REVISIÓN │
                    │  (Máx 3 intentos) │
                    └───────────────────┘
Flujo de Trabajo:
1.	Usuario envía un ticket de feature
2.	Planner descompone el ticket en tareas técnicas
3.	Coder genera el código para cada tarea
4.	Reviewer evalúa el código contra el plan
5.	Si aprueba → se entrega el código
6.	Si rechaza → el feedback vuelve al Coder (hasta 3 intentos)
________________________________________
 Estructura del Proyecto
ai-agents-pipeline/
├── backend/
│   ├── app/
│   │   ├── main.py              # API principal
│   │   ├── agents/
│   │   │   ├── base.py          # Clase base para agentes
│   │   │   ├── planner.py       # Agente Planner
│   │   │   ├── coder.py         # Agente Coder
│   │   │   └── reviewer.py      # Agente Reviewer
│   │   ├── orchestrator/
│   │   │   └── pipeline.py      # Orquestador de agentes
│   │   ├── models/
│   │   │   └── schemas.py       # Modelos Pydantic
│   │   └── utils/
│   │       └── logger.py        # Configuración de logs
│   ├── requirements.txt         # Dependencias
│   └── .env                     # Variables de entorno
├── frontend/
│   ├── index.html               # Interfaz de chat
│   ├── styles.css               # Estilos
│   └── script.js                # Lógica del frontend
├── runtime.txt                  # Versión de Python para Render
└── README.md                    # Este archivo
________________________________________
🚀 Cómo Correrlo Localmente
Requisitos Previos
•	Python 3.11 o superior
•	Una API Key de OpenRouter (gratis en openrouter.ai/keys)
Paso 1: Clonar el repositorio
bash
git clone https://github.com/CEALMEBA/Prueba-IA
cd Prueba-IA
Paso 2: Crear y configurar el archivo .env
bash
cp backend/.env.example backend/.env
Edita backend/.env con tu API Key:
env
OPENAI_API_KEY=sk-or-v1-tu_clave_aqui
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=ox/alpha
MAX_ATTEMPTS=3
Paso 3: Instalar dependencias
bash
pip install -r backend/requirements.txt
Paso 4: Ejecutar el servidor
bash
cd backend
uvicorn app.main:app --reload
Paso 5: Abrir la interfaz
Ve a http://localhost:8000 en tu navegador.
________________________________________
 Variables de Entorno Necesarias
Variable	Descripción	Ejemplo
OPENAI_API_KEY	API Key de OpenRouter	sk-or-v1-...
OPENAI_BASE_URL	URL de la API de OpenRouter	https://openrouter.ai/api/v1
MODEL_NAME	Modelo de IA a utilizar	ox/alpha
MAX_ATTEMPTS	Número máximo de intentos del Reviewer	3
________________________________________
📊 Tecnologías Utilizadas
Tecnología	Uso
FastAPI	API Backend
Uvicorn	Servidor ASGI
OpenAI SDK	Cliente para llamar a LLMs
OpenRouter	Proveedor de modelos de IA (gratis)
HTML/CSS/JS	Frontend interactivo
Render	Plataforma de despliegue
