#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 20:32:21 2025.

@author: vcsil
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import keyring

from utils import ENV

# Monta a URL de conexão a partir do .env
service = ENV["KEYRING_SERVICE"]

DB_PASSWORD = quote_plus(keyring.get_password(service, ENV["DB_NAME"]))

DB_URL = f"postgresql+psycopg://{ENV['DB_USER']}:{DB_PASSWORD}@"
DB_URL += f"{ENV['DB_HOST']}:{ENV['DB_PORT']}/{ENV['DB_NAME']}"

# Cria o "motor" de conexão
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

# Cria uma fábrica de sessões que serão usadas para interagir com o DB
SessionLocal = sessionmaker(bind=engine, autoflush=False,
                            expire_on_commit=False, class_=Session)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Gerencia transação e fechamento da sessão."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
