import logging
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

BRASIL_API_BASE_URL = "https://brasilapi.com.br/api"

async def fetch_cep_info(cep: str) -> Optional[Dict[str, Any]]:
    """
    Busca informações do CEP usando a BrasilAPI.
    Retorna um dicionário com os dados se encontrado, ou None caso contrário.
    """
    clean_cep = cep.replace("-", "").replace(".", "").strip()
    url = f"{BRASIL_API_BASE_URL}/cep/v1/{clean_cep}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                logger.info(f"CEP {cep} encontrado com sucesso na BrasilAPI.")
                return response.json()
            else:
                logger.warning(f"Erro ao buscar CEP {cep}: Status {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Exceção ao buscar CEP {cep}: {e}")
        return None

async def fetch_cnpj_info(cnpj: str) -> Optional[Dict[str, Any]]:
    """
    Busca informações do CNPJ usando a BrasilAPI.
    Retorna um dicionário com os dados cadastrais se encontrado, ou None caso contrário.
    """
    clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
    url = f"{BRASIL_API_BASE_URL}/cnpj/v1/{clean_cnpj}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                logger.info(f"CNPJ {cnpj} encontrado com sucesso na BrasilAPI.")
                return response.json()
            else:
                logger.warning(f"Erro ao buscar CNPJ {cnpj}: Status {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Exceção ao buscar CNPJ {cnpj}: {e}")
        return None

async def fetch_fipe_by_code(codigo_fipe: str) -> Optional[Dict[str, Any]]:
    """
    Busca informações de veículo na tabela FIPE usando a BrasilAPI pelo código FIPE.
    Retorna dados do veículo ou None.
    """
    clean_code = codigo_fipe.strip()
    url = f"{BRASIL_API_BASE_URL}/fipe/preco/v1/{clean_code}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Veículo com FIPE {codigo_fipe} encontrado com sucesso.")
                # BrasilAPI retorna uma lista de registros para o código FIPE
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                return data
            else:
                logger.warning(f"Erro ao buscar FIPE {codigo_fipe}: Status {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Exceção ao buscar FIPE {codigo_fipe}: {e}")
        return None
