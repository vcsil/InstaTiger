#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 21:21:59 2025.

@author: vcsil

instagram_client.py
Wrapper para criação e autenticação de um instagrapi.Client centralizado.

Recursos:
- Lê .env (INSTAGRAPI_SETTINGS_DIR, PROXY_URL, KEYRING_SERVICE,
           INSTAGRAPI_SESSION_MODE, TZ, INSTAGRAPI_LOCALE,
           INSTAGRAPI_COUNTRY, INSTAGRAPI_COUNTRY_CODE)
- Aplica cabeçalhos/regionais BR (locale, país, DDI, fuso horario)
- Persiste settings/cookies por usuário (<dir>/<username>.json)
- Autentica via sessionid OU password guardados no keyring
- Proxy: preparado, mas DESATIVADO (a pedido)

Requer:
- instagrapi
- python-dotenv
- keyring
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pathlib import Path
import logging
import json

from instagrapi import Client
import keyring

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # Último recurso (evitar quebra se ambiente muito antigo)

from utils import ENV

# ------------------------------------------------------
# Configuração de logging básica (ajuste conforme o projeto)
# ------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)


class InstagramAuthError(RuntimeError):
    """Erro de autenticação/configuração de credenciais."""


def _env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    """Help para ler variáveis de ambiente com default."""
    v = ENV[name]
    return v if (v is not None and str(v).strip() != "") else default


def _settings_path_for(username: str, base_dir: Path) -> Path:
    """Caminho do arquivo de settings por usuário."""
    safe = username.strip().lower()
    return base_dir / f"{safe}.json"


def _load_settings_if_exists(client: Client, settings_file: Path) -> bool:
    """Tenta carregar settings do arquivo. Retorna True se carregou."""
    if not settings_file.exists():
        return False
    try:
        # API do instagrapi suporta carregar direto do caminho
        client.load_settings(str(settings_file))
        logger.info("Settings carregados de: %s", settings_file)
        return True
    except Exception as e:
        logger.warning(
            "Falha ao carregar settings (%s). Vou ignorar e relogar.", e)
        # Se o arquivo estiver corrompido, opcionalmente apagar:
        try:
            # Verifica se é JSON inválido antes de remover
            json.loads(settings_file.read_text())
        except Exception:
            logger.warning("Settings inválidos; removendo arquivo: %s",
                           settings_file)
            settings_file.unlink(missing_ok=True)
        return False


def _dump_settings(client: Client, settings_file: Path) -> None:
    """Salva settings no caminho indicado."""
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    client.dump_settings(str(settings_file))
    logger.info("Settings salvos em: %s", settings_file)


def _login_with_sessionid(client: Client, username: str, service: str,
                          settings_file: Path) -> bool:
    """Tenta logar usando sessionid do keyring. Retorna True se conseguiu."""
    sessionid = keyring.get_password(service, f"{username}:sessionid")
    if not sessionid:
        return False
    try:
        client.login_by_sessionid(sessionid)
        # Se chegou aqui, sessão está válida
        _dump_settings(client, settings_file)
        logger.info("Autenticado via SESSIONID para @%s", username)
        return True
    except Exception as e:
        logger.warning("Falha login por SESSIONID para @%s: %s", username, e)
        return False


def _login_with_password(client: Client, username: str, service: str,
                         settings_file: Path) -> None:
    """Loga via password do keyring ou lança InstagramAuthError."""
    password = keyring.get_password(service, f"{username}:password")
    if not password:
        raise InstagramAuthError(
            f"Senha não encontrada no keyring (service='{service}'"
            f", key='{username}:password'). "
            "Use seu setup_credentials.py para salvar a senha."
        )
    try:
        client.login(username, password)
        _dump_settings(client, settings_file)
        logger.info("Autenticado via PASSWORD para @%s", username)
    except Exception as e:
        raise InstagramAuthError(
            f"Falha no login por senha para @{username}: {e}") from e


def _tz_offset_seconds_from_env() -> int:
    """
    Lê TZ (ex.: 'America/Sao_Paulo') e calcula o offset em segundos.

    Se ausente/indisponível, usa 'America/Sao_Paulo' como padrão.
    """
    tz_name = _env_str("TZ", "America/Sao_Paulo")
    # Fallback seguro se ZoneInfo indisponível
    if ZoneInfo is None:
        # UTC-3 padrão Brasil sudeste
        logger.warning(
            "ZoneInfo indisponível; assumindo offset -10800 (UTC-3).")
        return -10800
    try:
        tz = ZoneInfo(tz_name)
        offset = int(datetime.now(tz).utcoffset().total_seconds())
        return offset
    except Exception as e:
        logger.warning(
            "Falha ao resolver timezone '%s' (%s). Usando America/Sao_Paulo.",
            tz_name, e)
        tz = ZoneInfo("America/Sao_Paulo")
        return int(datetime.now(tz).utcoffset().total_seconds())


def _apply_regional_settings(client: Client) -> None:
    """
    Aplica cabeçalhos regionais no client.

    - Locale, país e DDI vindos do .env (ou defaults BR)
    - Offset de fuso calculado do timezone
    """
    locale = _env_str("INSTAGRAPI_LOCALE", "pt_BR")
    country = _env_str("INSTAGRAPI_COUNTRY", "BR")
    country_code = int(_env_str("INSTAGRAPI_COUNTRY_CODE", "55"))
    tz_offset = _tz_offset_seconds_from_env()

    client.set_locale(locale)
    client.set_country(country)
    client.set_country_code(country_code)
    client.set_timezone_offset(tz_offset)

    logger.info(
        "Regionais aplicados: locale=%s, country=%s, country_code=%s"
        ", tz_offset=%s",
        locale, country, country_code, tz_offset
    )

    # Alerta leve se offset não for o padrão BR sudeste (UTC-3 = -10800)
    if tz_offset != -10800:
        logger.warning(
            "Timezone offset != -10800 (UTC-3). "
            "Isso pode indicar que o host/proxy não é BR "
            "ou que o fuso configurado difere de America/Sao_Paulo."
        )


def build_client(username: str, *, force_relogin: bool = False) -> Client:
    """
    Cria e retorna um instagrapi.Client autenticado para `username`.

    Estratégia de autenticação (INSTAGRAPI_SESSION_MODE):
      - 'sessionid' : usa apenas sessionid do keyring
      - 'password'  : usa apenas password do keyring
      - 'auto' (padrão): tenta sessionid; se falhar, tenta password

    Persistência:
      - Settings/cookies ficam em <INSTAGRAPI_SETTINGS_DIR>/<username>.json

    Proxy:
      - Variável PROXY_URL é lida, mas IGNORADA por enquanto (não configuramos)

    Exceções:
      - InstagramAuthError para problemas de credenciais.
    """
    settings_dir = Path(
        _env_str("INSTAGRAPI_SETTINGS_DIR", ".instagrapi")
        ).expanduser().resolve()
    keyring_service = _env_str("KEYRING_SERVICE", "instabot")
    session_mode = (
        _env_str("INSTAGRAPI_SESSION_MODE", "auto") or "auto").strip().lower()
    proxy_url = _env_str("PROXY_URL", None)  # lido, mas não aplicado (a pedido

    logger.debug(
        "Config: settings_dir=%s, service=%s, mode=%s, proxy(ignored)=%s",
        settings_dir, keyring_service, session_mode, bool(proxy_url))

    c = Client()

    # (IGNORADO) Proxy: preparado, mas não aplicado no momento.
    # if proxy_url:
    #     c.set_proxy(proxy_url)

    # >>> APLICA REGIONAIS BR ANTES DE QUALQUER LOGIN/VALIDAÇÃO <<<
    _apply_regional_settings(c)

    settings_file = _settings_path_for(username, settings_dir)

    # 1) Carrega settings existentes (se válidos), a menos que
    # force_relogin=True
    loaded = False
    if not force_relogin:
        loaded = _load_settings_if_exists(c, settings_file)

    # 2) Se já carregou settings, tenta uma operação leve para validar sessão
    if loaded:
        try:
            # Uma chamada simples que exige sessão; se falhar, relogamos
            _ = c.account_info()
            logger.info("Sessão válida reaproveitada para @%s", username)
            return c
        except Exception as e:
            logger.info(
                "Sessão prévia inválida/expirada para @%s (%s); relogando.",
                username, e)

    # 3) Autenticação conforme modo escolhido
    if session_mode not in {"auto", "sessionid", "password"}:
        logger.warning("INSTAGRAPI_SESSION_MODE inválido: %s (usando 'auto')",
                       session_mode)
        session_mode = "auto"

    if session_mode in {"auto", "sessionid"}:
        if _login_with_sessionid(c, username, keyring_service, settings_file):
            return c
        if session_mode == "sessionid":
            raise InstagramAuthError(
                f"SESSIONID ausente/ineficaz para @{username}. "
                f"Salve-o no keyring (service='{keyring_service}'"
                f", key='{username}:sessionid') "
                "ou use INSTAGRAPI_SESSION_MODE=password/auto."
            )

    # Fallback (ou modo 'password'): tenta senha
    _login_with_password(c, username, keyring_service, settings_file)
    return c
