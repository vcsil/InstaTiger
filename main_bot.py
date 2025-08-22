#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 19:49:33 2025.

@author: vcsil
"""

from __future__ import annotations

import sys

from src.instagram_client import build_client
from utils import ENV


def run_login_test(username: str) -> None:
    """Loga via instagrapi e realiza uma chamada simples para validar."""
    try:
        cl = build_client(username)
        user_id = cl.user_id_from_username(username)
        cl.user_info(user_id)
        print(f"✅ Login OK para '{username}' (id={user_id}).")
    except Exception as exc:
        print(f"❌ Falha no login de '{username}': {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_login_test(sys.argv[1])
    else:
        username = ENV["ACCOUNTS"]
        if not username:
            print(
                "Uso: python main_bot.py <username> (ou defina ACCOUNTS no .env)",
                file=sys.stderr,
            )
            sys.exit(2)
        # Se houver múltiplos usuários em ACCOUNTS, usa o primeiro
        run_login_test(username.split(",")[0].strip())
