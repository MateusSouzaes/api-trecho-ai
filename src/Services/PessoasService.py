import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.Models.SharedModels import Pessoa, PessoaFisica
from src.Models.MotoristaPerfil import MotoristaPerfil
from src.Dtos.MotoristaDto import MotoristaCreate, MotoristaUpdate, MotoristaResponse

logger = logging.getLogger(__name__)

async def get_motorista_joined(session: AsyncSession, motorista_id: UUID, transportadora_id: UUID) -> MotoristaResponse:
    """Retorna os dados completos do motorista, unindo tabelas de public."""
    # Buscar motorista local da transportadora
    query_mot = select(MotoristaPerfil).where(
        MotoristaPerfil.id == motorista_id,
        MotoristaPerfil.transportadora_id == transportadora_id
    )
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
        cnh_pontos=mot.cnh_pontos,
        status_operacional=mot.status_operacional
    )

async def create_motorista(session: AsyncSession, data: MotoristaCreate, transportadora_id: UUID) -> MotoristaResponse:
    """
    Cadastra um motorista. Cria ou reutiliza registros físicos no schema public
    e cria o vínculo operacional na transportadora.
    """
    # 1. Verificar se CPF já existe no banco global (public)
    query_cpf = select(PessoaFisica).where(PessoaFisica.cpf == data.cpf)
    res_cpf = await session.execute(query_cpf)
    pf = res_cpf.scalar_one_or_none()

    pessoa_id = None
    if pf:
        pessoa_id = pf.pessoa_id
        # Verificar se esse motorista já possui registro na transportadora atual
        query_mot_exists = select(MotoristaPerfil).where(
            MotoristaPerfil.id == pessoa_id,
            MotoristaPerfil.transportadora_id == transportadora_id
        )
        res_mot_exists = await session.execute(query_mot_exists)
        if res_mot_exists.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Motorista com este CPF já cadastrado nesta transportadora."
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

    # 2. Criar Perfil de Motorista local
    mot = MotoristaPerfil(
        id=pessoa_id,
        transportadora_id=transportadora_id,
        cnh_numero=data.cnh_numero,
        cnh_categoria=data.cnh_categoria,
        cnh_validade=data.cnh_validade,
        cnh_pontos=data.cnh_pontos or 0,
        status_operacional=data.status_operacional or "DISPONIVEL"
    )
    session.add(mot)
    
    await session.commit()
    
    return await get_motorista_joined(session, pessoa_id, transportadora_id)

async def get_motoristas(session: AsyncSession, transportadora_id: UUID) -> List[MotoristaResponse]:
    """Retorna todos os motoristas cadastrados na transportadora."""
    query = select(MotoristaPerfil.id).where(MotoristaPerfil.transportadora_id == transportadora_id)
    res = await session.execute(query)
    ids = res.scalars().all()
    
    results = []
    for mid in ids:
        try:
            mot_joined = await get_motorista_joined(session, mid, transportadora_id)
            results.append(mot_joined)
        except Exception as e:
            logger.error(f"Erro ao juntar motorista {mid}: {e}")
            
    return results

async def update_motorista(session: AsyncSession, motorista_id: UUID, data: MotoristaUpdate, transportadora_id: UUID) -> MotoristaResponse:
    """Atualiza dados cadastrais e de habilitação de um motorista."""
    query_mot = select(MotoristaPerfil).where(
        MotoristaPerfil.id == motorista_id,
        MotoristaPerfil.transportadora_id == transportadora_id
    )
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

    # Atualizar dados do perfil
    if data.cnh_numero is not None:
        mot.cnh_numero = data.cnh_numero
    if data.cnh_categoria is not None:
        mot.cnh_categoria = data.cnh_categoria
    if data.cnh_validade is not None:
        mot.cnh_validade = data.cnh_validade
    if data.cnh_pontos is not None:
        mot.cnh_pontos = data.cnh_pontos
    if data.status_operacional is not None:
        mot.status_operacional = data.status_operacional

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

    return await get_motorista_joined(session, motorista_id, transportadora_id)

async def delete_motorista(session: AsyncSession, motorista_id: UUID, transportadora_id: UUID) -> None:
    """Remove a filiação do motorista deste tenant."""
    query_mot = select(MotoristaPerfil).where(
        MotoristaPerfil.id == motorista_id,
        MotoristaPerfil.transportadora_id == transportadora_id
    )
    res_mot = await session.execute(query_mot)
    mot = res_mot.scalar_one_or_none()
    if not mot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado."
        )
    await session.delete(mot)
    await session.commit()
