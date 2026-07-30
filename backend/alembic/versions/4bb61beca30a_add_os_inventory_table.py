"""Add os inventory table

Revision ID: 4bb61beca30a
Revises: 152747f4f71b
Create Date: 2026-07-30 10:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bb61beca30a'
down_revision: Union[str, Sequence[str], None] = '152747f4f71b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('operating_system_inventory',
    sa.Column('endpoint_id', sa.Uuid(), nullable=False),
    sa.Column('computer_name', sa.String(length=255), nullable=False),
    sa.Column('os_name', sa.String(length=255), nullable=False),
    sa.Column('edition', sa.String(length=255), nullable=False),
    sa.Column('version', sa.String(length=100), nullable=False),
    sa.Column('build_number', sa.String(length=100), nullable=False),
    sa.Column('display_version', sa.String(length=100), nullable=False),
    sa.Column('install_date', sa.String(length=100), nullable=False),
    sa.Column('last_boot_time', sa.String(length=100), nullable=False),
    sa.Column('uptime_seconds', sa.BigInteger(), nullable=False),
    sa.Column('system_architecture', sa.String(length=100), nullable=False),
    sa.Column('product_type', sa.String(length=100), nullable=False),
    sa.Column('registered_owner', sa.String(length=255), nullable=False),
    sa.Column('registered_organization', sa.String(length=255), nullable=False),
    sa.Column('windows_directory', sa.String(length=255), nullable=False),
    sa.Column('system_directory', sa.String(length=255), nullable=False),
    sa.Column('boot_device', sa.String(length=255), nullable=False),
    sa.Column('system_drive', sa.String(length=50), nullable=False),
    sa.Column('locale', sa.String(length=100), nullable=False),
    sa.Column('time_zone', sa.String(length=100), nullable=False),
    sa.Column('domain_workgroup', sa.String(length=255), nullable=False),
    sa.Column('activation_status', sa.String(length=255), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_operating_system_inventory_endpoint_id'), 'operating_system_inventory', ['endpoint_id'], unique=True)
    op.create_index(op.f('ix_operating_system_inventory_id'), 'operating_system_inventory', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_operating_system_inventory_id'), table_name='operating_system_inventory')
    op.drop_index(op.f('ix_operating_system_inventory_endpoint_id'), table_name='operating_system_inventory')
    op.drop_table('operating_system_inventory')
