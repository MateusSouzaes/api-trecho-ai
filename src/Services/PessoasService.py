import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.Models.SharedModels import Pessoa, PessoaFisica
from src.Models.Motorista import Motorista
from src.Dtos.MotoristaDto import MotoristaCreate, MotoristaUpdate, MotoristaResponse

logger = logging.getLogger(__name__)

async def get_motorista_joined(session: AsyncSession, motorista_id: UUID) -> MotoristaResponse:
    """Retorna os dados completos do motorista, unindo tabelas do tenant e public."""
    # Buscar motorista local no tenant
    query_mot = select(Motorista).where(Motorista.id == motorista_id)
    res_mot = await session.execute(query_mot)
    mot = res_mot.scalar_one_or_none()
    if not mot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado."
        )

    # Buscar dados de pessoa no público
    query_pf = select(PessoaFisica, Pessoa).join(Pessoa, Pessoa.id == PessoaFisica.pessoa_id).where(PessoaFisica.pessoa_id == motorista_id)
    res_pf = await session.execute(query_pf)
    pf_row = res_pf.first()
    if not pf_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro físico do motorista ausente."
        )
    pf, pes = pf_row

    return MotoristaResponse(
        id=mot.id,
        nome=pes.nome_razao_social,
        telefone=pes.telefone,
        email=pes.email,
        cpf=pf.cpf,
        rg=pf.rg,
        data_nascimento=pf.data_nascimento,
        cnh_numero=mot.cnh_numero,
        cnh_categoria=mot.cnh_categoria,
        cnh_validade=mot.cnh_validade,
        status=mot.status
    )

async def create_motorista(session: AsyncSession, data: MotoristaCreate) -> MotoristaResponse:
    """
    Cadastra um motorista. Cria ou reutiliza registros físicos no schema public
    e cria o vínculo operacional no tenant.
    """
    # 1. Verificar se CPF já existe no banco global (public)
    query_cpf = select(PessoaFisica).where(PessoaFisica.cpf == data.cpf)
    res_cpf = await session.execute(query_cpf)
    pf = res_cpf.scalar_one_or_none()

    pessoa_id = None
    if pf:
        pessoa_id = pf.pessoa_id
        # Verificar se esse motorista já possui registro no tenant atual
        query_mot_exists = select(Motorista).where(Motorista.id == pessoa_id)
        res_mot_exists = await session.execute(query_mot_exists)
        if res_mot_exists.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Motorista com este CPF já cadastrado neste tenant."
            )
    else:
        # Criar Pessoa Geral (public)
        pes = Pessoa(
            tipo_pessoa="FISICA",
            nome_razao_social=data.nome,
            telefone=data.telefone,
            email=data.email
        )
        session.add(pes)
        await session.flush()
        pessoa_id = pes.id

        # Criar Pessoa Física (public)
        pf = PessoaFisica(
            pessoa_id=pessoa_id,
            cpf=data.cpf,
            rg=data.rg,
            data_nascimento=data.data_nascimento
        )
        session.add(pf)
        await session.flush()

    # 2. Criar Motorista local (tenant)
    mot = Motorista(
        id=pessoa_id,
        cnh_numero=data.cnh_numero,
        cnh_categoria=data.cnh_categoria,
        cnh_validade=data.cnh_validade,
        status=data.status or "ATIVA"
    )
    session.add(mot)
    
    await session.commit()
    
    return await get_motorista_joined(session, pessoa_id)

async def get_motoristas(session: AsyncSession) -> List[MotoristaResponse]:
    """Retorna todos os motoristas cadastrados no tenant."""
    # Listar IDs locais do tenant
    query = select(Motorista.id)
    res = await session.execute(query)
    ids = res.scalars().all()
    
    results = []
    for mid in ids:
        try:
            mot_joined = await get_motorista_joined(session, mid)
            results.append(mot_joined)
        except Exception as e:
            logger.error(f"Erro ao juntar motorista {mid}: {e}")
            
    return results

async def update_motorista(session: AsyncSession, motorista_id: UUID, data: MotoristaUpdate) -> MotoristaResponse:
    """Atualiza dados cadastrais e de habilitação de um motorista."""
    # Buscar motorista local (para garantir 404 se não existir)
    query_mot = select(Motorista).where(Motorista.id == motorista_id)
    res_mot = await session.execute(query_mot)
    mot = res_mot.scalar_one_or_none()
    if not mot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado."
        )

    # Buscar dados de pessoa no público
    query_pf = select(PessoaFisica, Pessoa).join(Pessoa, Pessoa.id == PessoaFisica.pessoa_id).where(PessoaFisica.pessoa_id == motorista_id)
    res_pf = await session.execute(query_pf)
    pf_row = res_pf.first()
    if not pf_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dados físicos ausentes.")
    pf, pes = pf_row

    # Atualizar dados do tenant
    if data.cnh_numero is not None:
        mot.cnh_numero = data.cnh_numero
    if data.cnh_categoria is not None:
        mot.cnh_categoria = data.cnh_categoria
    if data.cnh_validade is not None:
        mot.cnh_validade = data.cnh_validade
    if data.status is not None:
        mot.status = data.status

    # Atualizar dados públicos
    if data.nome is not None:
        pes.nome_razao_social = data.nome
    if data.telefone is not None:
        pes.telefone = data.telefone
    if data.email is not None:
        pes.email = data.email

    session.add(mot)
    session.add(pes)
    await session.commit()

    return await get_motorista_joined(session, motorista_id)

async def delete_motorista(session: AsyncSession, motorista_id: UUID) -> None:
    """Remove a filiação do motorista deste tenant."""
    query_mot = select(Motorista).where(Motorista.id == motorista_id)
    res_mot = await session.execute(query_mot)
    mot = res_mot.scalar_one_or_none()
    if not mot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado."
        )
    await session.delete(mot)
    await session.commit()
