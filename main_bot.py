#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 19:49:33 2025.

@author: vcsil
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
import keyring
import sys

from instapy import InstaPy, smart_run  # contexto que faz login/logout

from utils import ENV

# ---------- Config ----------


@dataclass
class Settings:
    """Configurações do InstaPy."""

    service: str
    headless: bool
    browser: str               # "chrome" | "firefox"
    proxy_address: str | None
    proxy_port: int | None
    proxy_username: str | None
    proxy_password: str | None
    geckodriver_path: str | None
    chromedriver_path: str | None
    browser_executable_path: str | None


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "t", "yes", "y")


def load_settings() -> Settings:
    """Carrega configurações."""
    service = ENV["KEYRING_SERVICE"]
    headless = _parse_bool(ENV["INSTAPY_HEADLESS"], False)
    browser = (ENV["BROWSER"] or "chrome").strip().lower()

    # Proxy (opcional)
    proxy_url = None  # ENV["PROXY_URL"]
    p_addr = p_port = p_user = p_pass = None
    if proxy_url:
        u = urlparse(proxy_url)
        p_addr = u.hostname
        p_port = u.port
        if u.username:
            p_user = u.username
        if u.password:
            p_pass = u.password

    return Settings(
        service=service,
        headless=headless,
        browser=browser,
        proxy_address=p_addr,
        proxy_port=int(p_port) if p_port else None,
        proxy_username=p_user,
        proxy_password=p_pass,
        geckodriver_path=None,  # ENV["GECKODRIVER_PATH"],
        chromedriver_path=None,  # ENV["CHROMEDRIVER_PATH"],
        browser_executable_path=None,  # ENV["BROWSER_EXECUTABLE_PATH"],
    )

# ---------- Execução ----------


def run_login_test(username: str) -> None:
    """Faz login e encerra. Sem ações adicionais.

    - Busca a senha no keyring.
    - Respeita headless e navegador do .env.
    """
    cfg = load_settings()

    password = keyring.get_password(cfg.service, username)
    if not password:
        print(f"❌ Senha não encontrada no keyring para '{username}'. "
              f"Execute: python setup_credentials.py", file=sys.stderr)
        sys.exit(1)

    use_firefox = cfg.browser == "firefox"

    # Parâmetros suportados pelo InstaPy (Chrome é padrão; Firefox via
    # use_firefox)
    # Headless é suportado; se tiver problemas no primeiro login, deixe False.
    # Para Chrome, o pacote instapy-chromedriver cuida do driver. Para Firefox,
    # informe geckodriver_path se necessário.
    session = InstaPy(
        username=username,
        password=password,
        headless_browser=cfg.headless,
        # use_firefox=use_firefox,
        proxy_address=cfg.proxy_address,
        proxy_port=cfg.proxy_port,
        proxy_username=cfg.proxy_username,
        proxy_password=cfg.proxy_password,
        geckodriver_path=cfg.geckodriver_path,
        browser_executable_path=cfg.browser_executable_path,
        # Para Chrome, normalmente não precisa passar o caminho do chromedriver
        # se usar instapy-chromedriver.
    )

    # O smart_run cuida de: abrir navegador, realizar login, e encerrar sessão
    # com segurança.
    # Dentro do bloco você poderia executar outras ações; aqui só validamos o
    # login.
    try:
        with smart_run(session):
            print(f"✅ Login OK para '{username}'.")
            # Nenhuma ação — é apenas um teste de autenticação.
    except Exception as exc:
        print(f"❌ Falha no login de '{username}': {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
# =============================================================================
#     if len(sys.argv) < 2:
#         print("Uso: python3 main_bot.py <username>")
#         print("Necessário colocar o nome do usuario.")
#         sys.exit(2)
#     run_login_test(sys.argv[1])
# =============================================================================
    run_login_test(ENV["ACCOUNTS"])
