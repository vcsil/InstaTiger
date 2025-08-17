#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 19:57:35 2025.

@author: vcsil
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional, List


import sqlalchemy as sa
from sqlalchemy import (Integer, String, DateTime, UniqueConstraint,
                        BigInteger, Boolean, ForeignKey, Enum, Index, Text)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarativa que nossos modelos herdarão."""

    pass


class ActionType(str, enum.Enum):
    """Tipos de ações que podem ser realizadas."""

    follow = "follow"
    unfollow = "unfollow"
    login = "login"
    scan = "scan"


class ActionStatus(str, enum.Enum):
    """Representar o estado de processamento de uma ação."""

    pending = "pending"
    done = "done"
    failed = "failed"
    skipped = "skipped"


class SourceTypes(str, enum.Enum):
    """Representa a origem da busca."""

    hashtag = "hashtag"
    user = "user"
    location = "location"


class Account(Base):
    """Representa cada conta do Instagram gerenciada pelo sistema."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                            server_default=sa.text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.text("timezone('utc', now())"))

    actions: Mapped[List["ActionLog"]] = relationship(
        back_populates="account", cascade="all, delete-orphan")
    relationships: Mapped[List["Relationship"]] = relationship(
        back_populates="account", cascade="all, delete-orphan")


class Target(Base):
    """
    Representa um perfil alvo (@handle) que podemos seguir / deixar de seguir.

    com metadados de origem (hashtag, usuário, localização).
    """

    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    handle: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    source_type: Mapped[SourceTypes] = mapped_column(
        Enum(SourceTypes, name="source_types", native_enum=True),
        nullable=False, index=True)
    source_value: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.text("timezone('utc', now())"))

    actions: Mapped[List["ActionLog"]] = relationship(back_populates="target")
    relationships: Mapped[List["Relationship"]] = relationship(
        back_populates="target")


class Relationship(Base):
    """
    Estado atual da relação conta -> alvo (se estamos seguindo.

    Se houve follow back, etc.).
    Ajuda a decidir quem 'não segue de volta' para *unfollow*.
    """

    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint("account_id", "target_id",
                         name="uq_relationship_account_target"),
        Index("ix_relationship_followed_back", "account_id", "is_following",
              "followed_back"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey(
        "accounts.id", ondelete="CASCADE"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey(
        "targets.id", ondelete="CASCADE"), nullable=False)

    is_following: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                               server_default=sa.text("false"))
    followed_back: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                                server_default=sa.text("false")
                                                )

    followed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))
    follow_back_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))
    unfollowed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))

    account: Mapped["Account"] = relationship(back_populates="relationships")
    target: Mapped["Target"] = relationship(back_populates="relationships")


class ActionLog(Base):
    """Log de cada ação (follow/unfollow/etc.), com status e erro."""

    __tablename__ = "action_logs"
    __table_args__ = (
        Index("ix_action_account_created", "account_id", "created_at"),
        Index("ix_action_type_status", "type", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey(
        "accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("targets.id", ondelete="SET NULL"))

    type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_type", native_enum=True),
        nullable=False, index=True)

    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name="action_status", native_enum=True),
        nullable=False, index=True,
        server_default=sa.text(f"'{ActionStatus.pending.value}'"),
        default=ActionStatus.pending)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=sa.text("timezone('utc', now())"),
        default=lambda: datetime.now(timezone.utc))

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    account: Mapped["Account"] = relationship(back_populates="actions")
    target: Mapped[Optional["Target"]] = relationship(back_populates="actions")
