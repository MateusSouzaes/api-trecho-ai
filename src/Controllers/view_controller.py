from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(tags=["Views Frontend"])

# Obter o caminho completo para a pasta static
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

def read_html_file(filename: str) -> str:
    path = os.path.join(STATIC_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>Erro: O arquivo '{filename}' não foi encontrado na pasta static.</h1>"

@router.get("/login", response_class=HTMLResponse)
async def get_login_view():
    return read_html_file("login.html")

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_view():
    return read_html_file("dashboard.html")

@router.get("/pessoas", response_class=HTMLResponse)
async def get_pessoas_view():
    return read_html_file("pessoas.html")

@router.get("/frota", response_class=HTMLResponse)
async def get_frota_view():
    return read_html_file("frota.html")

@router.get("/whatsapp", response_class=HTMLResponse)
async def get_whatsapp_view():
    return read_html_file("whatsapp.html")

@router.get("/viagens", response_class=HTMLResponse)
async def get_viagens_view():
    return read_html_file("viagens.html")
