#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 12:08:27 2025.

@author: vcsil
"""

from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, text

from database.database import DB_URL


def main() -> None:
    """Função para verificar se o banco de dados existe."""
    # cria o banco se não existir
    if not database_exists(DB_URL):
        print("Cria Banco de dados")
        create_database(DB_URL)

    engine = create_engine(DB_URL, pool_pre_ping=True)
    # Testa conezão com banco
    with engine.connect() as conn:
        # teste simples
        result = conn.execute(text("select 1")).scalar_one()
        print("OK, SELECT 1 ->", result)


if __name__ == "__main__":
    main()
