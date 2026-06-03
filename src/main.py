"""
Ponto de entrada da aplicação FastAPI.
Inicializa a aplicação, define middlewares e agrupa os routers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.DataContexts.DatabaseContext import init_db, close_db

# Importar routers dos Controllers
from src.Controllers.AuthController import router as auth_router
from src.Controllers.FrotaController import router as frota_router
from src.Controllers.PessoasController import router as pessoas_router
from src.Controllers.ViagensController import router as viagens_router
from src.Controllers.DashboardController import router as dashboard_router
from src.Controllers.WhatsappController import router as whatsapp_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    - Startup: Inicializa o banco de dados
    - Shutdown: Fecha a conexão com o banco
    """
    # STARTUP
    logger.info("🚀 Iniciando Trecho.ai API...")
    await init_db()
    logger.info("✅ API iniciada com sucesso!")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Encerrando Trecho.ai API...")
    await close_db()
    logger.info("✅ API encerrada")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restringir em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(frota_router)
app.include_router(pessoas_router)
app.include_router(viagens_router)
app.include_router(dashboard_router)
app.include_router(whatsapp_router)


# Rotas de Health Check
@app.get("/")
async def read_root():
    return {
        "status": "Trecho.ai operando a todo vapor! 🚛",
        "version": settings.app_version
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2026-05-14T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )