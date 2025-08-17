#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 19:34:48 2025.

Script para cadastrar as senhas das contas Instagram no keyring do SO.

@author: vcsil
"""

import getpass
import keyring

from utils import ENV


def main():
    """Faz o gerenciamento segura das senhas das contas e do banco."""
    service = ENV["KEYRING_SERVICE"]

    accounts = ENV["DB_NAME"] + "," + ENV["ACCOUNTS"]
    if not accounts:
        print("⚠️  Variável ACCOUNTS ou DB_NAME vazia no .env")
        return

    # 2) Para cada usuário listado, solicita senha e grava no keyring
    for username in [u.strip() for u in accounts.split(",") if u.strip()]:
        prompt = f"Senha para '{username}': "
        password = getpass.getpass(prompt)
        keyring.set_password(service, username, password)
        print(f"🔒 Credencial armazenada para: {username}")

    print("\n✅ Todas as credenciais foram cadastradas com sucesso!")


if __name__ == "__main__":
    main()
