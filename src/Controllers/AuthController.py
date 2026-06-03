from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.DataContexts.DatabaseContext import get_session, get_current_user
from src.Models.Usuario import Usuario
from src.Dtos.AuthDto import TransportadoraRegister, TokenResponse, UsuarioResponse, LoginRequest
from src.Services import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: TransportadoraRegister,
    session: AsyncSession = Depends(get_session)
):
    """
    Cadastra uma nova transportadora (tenant), cria as tabelas no banco de dados
    e gera o usuário administrador.
    """
    usuario = await AuthService.register_new_tenant(data, session)
    return UsuarioResponse.model_validate(usuario)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Realiza o login de um usuário e gera um token JWT de acesso.
    """
    token_resp = await AuthService.authenticate_user(data, session)
    return token_resp

@router.get("/me", response_model=UsuarioResponse)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna as informações do perfil do usuário autenticado no momento.
    """
    return UsuarioResponse.model_validate(current_user)
