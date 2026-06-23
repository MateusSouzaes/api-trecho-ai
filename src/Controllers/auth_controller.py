from fastapi import APIRouter, Depends, status

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.auth_dto import TransportadoraRegister, TokenResponse, UsuarioResponse, LoginRequest
from src.services import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: TransportadoraRegister,
    auth_service: AuthService = Depends()
):
    """
    Cadastra uma nova transportadora (tenant), cria as tabelas no banco de dados
    e gera o usuário administrador.
    """
    usuario = await auth_service.register_new_tenant(data)
    return UsuarioResponse.model_validate(usuario)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends()
):
    """
    Realiza o login de um usuário e gera um token JWT de acesso.
    """
    token_resp = await auth_service.authenticate_user(data)
    return token_resp

@router.get("/me", response_model=UsuarioResponse)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna as informações do perfil do usuário autenticado no momento.
    """
    return UsuarioResponse.model_validate(current_user)
