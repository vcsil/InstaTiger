#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 19:34:48 2025.

Script para cadastrar as senhas das contas Instagram no keyring do SO.

@author: vcsil
"""
import sys
import getpass
import keyring

from utils import ENV


def set_cred(service: str, username: str, password: str | None = None,
             sufix: str = "") -> None:
    """Salva a credencial."""
    if not password:
        password = getpass.getpass(f"Senha para '{username}': ")
    keyring.set_password(service, username+sufix, password)
    print(f"🔒 Credencial armazenada para: {username}")


def main():
    """Faz o gerenciamento segura das senhas das contas e do banco."""
    service = ENV["KEYRING_SERVICE"]

    # Modo via CLI: ./setup_credentials.py usuario [senha]
    if len(sys.argv) >= 2:
        username = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) >= 3 else None
        set_cred(service, username, password)
        return

    accounts = ENV["DB_NAME"] + "," + ENV["ACCOUNTS"]
    if not accounts:
        print("⚠️  Variável ACCOUNTS ou DB_NAME vazia no .env")
        return

    # 2) Para cada usuário listado, solicita senha e grava no keyring
    for idx, username in enumerate(
            [u.strip() for u in accounts.split(",") if u.strip()]):
        sufix = ":password" if idx > 0 else ""
        set_cred(service, username, None, sufix)

    print("\n✅ Todas as credenciais foram cadastradas com sucesso!")


if __name__ == "__main__":
    main()
