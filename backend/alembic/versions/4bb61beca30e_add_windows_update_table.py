"""Add windows update inventory table

Revision ID: 4bb61beca30e
Revises: 4bb61beca30d
Create Date: 2026-07-30 11:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4bb61beca30e"
down_revision: Union[str, Sequence[str], None] = "4bb61beca30d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "windows_update_inventory",
        sa.Column("endpoint_id", sa.Uuid(), nullable=False),
        sa.Column("kb_number", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("installed_by", sa.String(length=255), nullable=False),
        sa.Column("installed_on", sa.String(length=100), nullable=False),
        sa.Column("support_url", sa.String(length=500), nullable=False),
        sa.Column("update_id", sa.String(length=100), nullable=False),
        sa.Column("revision_number", sa.BigInteger(), nullable=False),
        sa.Column("operation_result", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("is_security_update", sa.Boolean(), nullable=False),
        sa.Column("is_critical_update", sa.Boolean(), nullable=False),
        sa.Column("is_feature_update", sa.Boolean(), nullable=False),
        sa.Column("is_cumulative_update", sa.Boolean(), nullable=False),
        sa.Column("requires_restart", sa.Boolean(), nullable=False),
        sa.Column("is_hidden", sa.Boolean(), nullable=False),
        sa.Column("is_downloaded", sa.Boolean(), nullable=False),
        sa.Column("installed_state", sa.String(length=100), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["endpoint_id"], ["endpoints.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_windows_update_inventory_category"),
        "windows_update_inventory",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_windows_update_inventory_endpoint_id"),
        "windows_update_inventory",
        ["endpoint_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_windows_update_inventory_id"),
        "windows_update_inventory",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_windows_update_inventory_installed_on"),
        "windows_update_inventory",
        ["installed_on"],
        unique=False,
    )
    op.create_index(
        op.f("ix_windows_update_inventory_kb_number"),
        "windows_update_inventory",
        ["kb_number"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_windows_update_inventory_kb_number"),
        table_name="windows_update_inventory",
    )
    op.drop_index(
        op.f("ix_windows_update_inventory_installed_on"),
        table_name="windows_update_inventory",
    )
    op.drop_index(
        op.f("ix_windows_update_inventory_id"), table_name="windows_update_inventory"
    )
    op.drop_index(
        op.f("ix_windows_update_inventory_endpoint_id"),
        table_name="windows_update_inventory",
    )
    op.drop_index(
        op.f("ix_windows_update_inventory_category"),
        table_name="windows_update_inventory",
    )
    op.drop_table("windows_update_inventory")
