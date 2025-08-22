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


def _ask_suffix(username: str) -> str:
    """Pergunta ao usuário o tipo de credencial para ``username``.

    Retorna ``":password"`` ou ``":sessionid"``.
    """
    while True:
        choice = input(
            f"Para '{username}', digite 'senha' ou 'sessionid': "
        ).strip().lower()
        if choice in {"senha", "sessionid"}:
            return ":password" if choice == "senha" else ":sessionid"
        print("Entrada inválida. Tente novamente.")


def set_cred(service: str, username: str, secret: str | None = None,
             sufix: str = "") -> None:
    """Salva a credencial."""
    label = "sessionid" if sufix == ":sessionid" else "senha"
    if not secret:
        secret = getpass.getpass(f"{label.capitalize()} para '{username}': ")
    keyring.set_password(service, username+sufix, secret)
    print(f"🔒 Credencial armazenada para: {username}")


def main():
    """Faz o gerenciamento segura das senhas das contas e do banco."""
    service = ENV["KEYRING_SERVICE"]

    # Modo via CLI: ./setup_credentials.py usuario [senha|sessionid] [tipo]
    if len(sys.argv) >= 2:
        username = sys.argv[1]
        secret = sys.argv[2] if len(sys.argv) >= 3 else None
        cred_type = sys.argv[3] if len(sys.argv) >= 4 else "senha"
        if cred_type not in {"senha", "sessionid"}:
            print("⚠️  Tipo inválido. Use 'senha' ou 'sessionid'.")
            return

        if username == ENV["DB_NAME"]:
            if cred_type != "senha":
                print("⚠️  DB_NAME só aceita 'senha'.")
                return
            sufix = ""
        else:
            sufix = ":password" if cred_type == "senha" else ":sessionid"

        set_cred(service, username, secret)
        return

    accounts = ENV["DB_NAME"] + "," + ENV["ACCOUNTS"]
    if not accounts:
        print("⚠️  Variável ACCOUNTS ou DB_NAME vazia no .env")
        return

    # 2) Para cada usuário listado, solicita credencial e grava no keyring
    for idx, username in enumerate(
            [u.strip() for u in accounts.split(",") if u.strip()]):

        if idx == 0:
            # Banco de dados: apenas senha
            set_cred(service, username)
            continue

        sufix = _ask_suffix(username)
        set_cred(service, username, None, sufix)

    print("\n✅ Todas as credenciais foram cadastradas com sucesso!")


if __name__ == "__main__":
    main()
