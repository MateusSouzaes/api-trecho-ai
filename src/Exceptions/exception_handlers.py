import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class BusinessException(Exception):
    """Exceção customizada para regras de negócio violadas."""
    def __init__(self, detail: str, error_code: str, status_code: int = 400):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)

def setup_exception_handlers(app: FastAPI) -> None:
    """Registra os manipuladores de exceções globais na aplicação FastAPI."""
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.detail,
                    "code": exc.error_code
                }
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        code_map = {
            404: "NOT_FOUND",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            400: "BAD_REQUEST",
            422: "VALIDATION_ERROR"
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.detail,
                    "code": error_code
                }
            }
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        logger.error(f"Erro de integridade de banco de dados: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "message": "Erro de integridade relacional no banco de dados.",
                    "code": "INTEGRITY_ERROR"
                }
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Erro interno não tratado: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "message": "Erro interno inesperado no servidor.",
                    "code": "INTERNAL_SERVER_ERROR"
                }
            }
        )
