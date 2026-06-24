from fastapi import APIRouter, Depends, status
from typing import List

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.fornecedor_dto import FornecedorCreate, FornecedorResponse
from src.services.fornecedor_service import FornecedorService

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores (Parceiros)"])

@router.post("", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
async def create_fornecedor(
    data: FornecedorCreate,
    current_user: Usuario = Depends(get_current_user),
    service: FornecedorService = Depends()
):
    record = await service.create_fornecedor(data, current_user.transportadora_id)
    return record

@router.get("", response_model=List[FornecedorResponse])
async def get_fornecedores(
    current_user: Usuario = Depends(get_current_user),
    service: FornecedorService = Depends()
):
    records = await service.get_fornecedores(current_user.transportadora_id)
    return records
