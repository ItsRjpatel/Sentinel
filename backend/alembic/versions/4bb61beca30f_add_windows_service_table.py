"""Add windows service inventory table

Revision ID: 4bb61beca30f
Revises: 4bb61beca30e
Create Date: 2026-07-30 11:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bb61beca30f'
down_revision: Union[str, Sequence[str], None] = '4bb61beca30e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('windows_service_inventory',
    sa.Column('endpoint_id', sa.Uuid(), nullable=False),
    sa.Column('service_name', sa.String(length=255), nullable=False),
    sa.Column('display_name', sa.String(length=500), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('executable_path', sa.String(length=1000), nullable=False),
    sa.Column('current_state', sa.String(length=50), nullable=False),
    sa.Column('start_mode', sa.String(length=50), nullable=False),
    sa.Column('start_type', sa.String(length=50), nullable=False),
    sa.Column('service_type', sa.String(length=100), nullable=False),
    sa.Column('account_name', sa.String(length=255), nullable=False),
    sa.Column('process_id', sa.BigInteger(), nullable=False),
    sa.Column('binary_path', sa.String(length=1000), nullable=False),
    sa.Column('delayed_auto_start', sa.Boolean(), nullable=False),
    sa.Column('error_control', sa.String(length=50), nullable=False),
    sa.Column('dependencies', sa.String(length=1000), nullable=False),
    sa.Column('dependent_services', sa.String(length=1000), nullable=False),
    sa.Column('can_stop', sa.Boolean(), nullable=False),
    sa.Column('can_pause', sa.Boolean(), nullable=False),
    sa.Column('can_shutdown', sa.Boolean(), nullable=False),
    sa.Column('desktop_interaction', sa.Boolean(), nullable=False),
    sa.Column('tag_id', sa.BigInteger(), nullable=False),
    sa.Column('is_critical', sa.Boolean(), nullable=False),
    sa.Column('digital_signature_status', sa.String(length=255), nullable=False),
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
    op.create_index(op.f('ix_windows_service_inventory_current_state'), 'windows_service_inventory', ['current_state'], unique=False)
    op.create_index(op.f('ix_windows_service_inventory_endpoint_id'), 'windows_service_inventory', ['endpoint_id'], unique=False)
    op.create_index(op.f('ix_windows_service_inventory_id'), 'windows_service_inventory', ['id'], unique=False)
    op.create_index(op.f('ix_windows_service_inventory_service_name'), 'windows_service_inventory', ['service_name'], unique=False)
    op.create_index(op.f('ix_windows_service_inventory_start_mode'), 'windows_service_inventory', ['start_mode'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_windows_service_inventory_start_mode'), table_name='windows_service_inventory')
    op.drop_index(op.f('ix_windows_service_inventory_service_name'), table_name='windows_service_inventory')
    op.drop_index(op.f('ix_windows_service_inventory_id'), table_name='windows_service_inventory')
    op.drop_index(op.f('ix_windows_service_inventory_endpoint_id'), table_name='windows_service_inventory')
    op.drop_index(op.f('ix_windows_service_inventory_current_state'), table_name='windows_service_inventory')
    op.drop_table('windows_service_inventory')
