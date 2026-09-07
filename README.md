# AI Agents Pipeline - Sistema Multi-Agente

## Visión General

Sistema de agentes colaborativos que transforma tickets de features en código funcional. Utiliza tres agentes especializados (Planner, Coder, Reviewer) que trabajan en conjunto para descomponer requisitos, implementar soluciones y validar resultados con un loop automático de revisión y mejora.

## Arquitectura
[Usuario] → [Frontend] → [API] → [Orquestador]
↓
[Planner Agent]
↓
[Coder Agent] ←→ [Reviewer Agent]
↓
(Loop de revisión)
↓
[Respuesta al usuario]


## Características Principales

- ✅ Pipeline multi-agente con 3 roles especializados
- 🔄 Loop automático de revisión con reintentos configurables
- 💬 Interfaz de chat multi-turno con contexto persistente
- 📊 Logs de ejecución para trazabilidad
- 🚀 Desplegable con Docker

## Requisitos Técnicos

- Python 3.11+
- OpenAI API Key(api gratuita o cualquier otro modelo)
- Docker (opcional)

## Instalación Local

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd ai-agents-pipeline

cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

pip install -r requirements.txt

#ejeutar localmente 
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

#deliegue en docker 
docker-compose up -d