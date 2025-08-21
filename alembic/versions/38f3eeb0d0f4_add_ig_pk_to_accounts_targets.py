"""add ig_pk to accounts/targets.

Revision ID: 38f3eeb0d0f4
Revises: 8f4e2538a646
Create Date: 2025-08-19 16:37:23.743787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38f3eeb0d0f4'
down_revision: Union[str, Sequence[str], None] = '8f4e2538a646'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # accounts.ig_pk BIGINT NULL UNIQUE
    op.add_column("accounts", sa.Column("ig_pk", sa.BigInteger(),
                                        nullable=True))
    op.create_unique_constraint("uq_accounts_ig_pk", "accounts", ["ig_pk"])

    # targets.ig_pk BIGINT NULL + índice único parcial (ig_pk IS NOT NULL)
    op.add_column("targets", sa.Column("ig_pk", sa.BigInteger(),
                                       nullable=True))
    op.create_index("uq_targets_ig_pk_not_null", "targets", ["ig_pk"],
                    unique=True, postgresql_where=sa.text("ig_pk IS NOT NULL"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_targets_ig_pk_not_null", table_name="targets")
    op.drop_column("targets", "ig_pk")

    op.drop_constraint("uq_accounts_ig_pk", "accounts", type_="unique")
    op.drop_column("accounts", "ig_pk")
