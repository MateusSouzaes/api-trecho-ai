from src.data_contexts.database_context import get_current_tenant_session
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status

from src.models.shared_models import Pessoa, PessoaJuridica
from src.models.fornecedor import Fornecedor
from src.dtos.fornecedor_dto import FornecedorCreate

class FornecedorService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def create_fornecedor(self, data: FornecedorCreate, transportadora_id: UUID) -> dict:
        # 1. Create Pessoa JURIDICA
        pessoa = Pessoa(
            tipo_pessoa="JURIDICA",
            nome_razao_social=data.nome_razao_social,
            telefone=data.telefone,
            email=data.email
        )
        self.session.add(pessoa)
        await self.session.flush()

        pessoa_juridica = PessoaJuridica(
            pessoa_id=pessoa.id,
            cnpj=data.cnpj,
            nome_fantasia=data.nome_razao_social
        )
        self.session.add(pessoa_juridica)
        await self.session.flush()

        # 2. Create Fornecedor
        fornecedor = Fornecedor(
            transportadora_id=transportadora_id,
            pessoa_id=pessoa.id,
            categoria=data.categoria,
            status="ATIVO"
        )
        self.session.add(fornecedor)
        await self.session.commit()
        await self.session.refresh(fornecedor)
        
        return {
            "id": fornecedor.id,
            "transportadora_id": fornecedor.transportadora_id,
            "pessoa_id": fornecedor.pessoa_id,
            "nome_razao_social": data.nome_razao_social,
            "categoria": fornecedor.categoria,
            "status": fornecedor.status
        }

    async def get_fornecedores(self, transportadora_id: UUID) -> List[dict]:
        query = select(Fornecedor, Pessoa).join(Pessoa, Fornecedor.pessoa_id == Pessoa.id).where(Fornecedor.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        records = []
        for forn, pes in result.all():
            records.append({
                "id": forn.id,
                "transportadora_id": forn.transportadora_id,
                "pessoa_id": forn.pessoa_id,
                "nome_razao_social": pes.nome_razao_social,
                "categoria": forn.categoria,
                "status": forn.status
            })
        return records
