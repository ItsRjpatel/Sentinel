"""Add storage inventory tables

Revision ID: 4bb61beca30c
Revises: 4bb61beca30b
Create Date: 2026-07-30 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bb61beca30c'
down_revision: Union[str, Sequence[str], None] = '4bb61beca30b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('physical_disk_inventory',
    sa.Column('endpoint_id', sa.Uuid(), nullable=False),
    sa.Column('disk_number', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(length=255), nullable=False),
    sa.Column('manufacturer', sa.String(length=255), nullable=False),
    sa.Column('serial_number', sa.String(length=255), nullable=False),
    sa.Column('firmware_version', sa.String(length=100), nullable=False),
    sa.Column('media_type', sa.String(length=50), nullable=False),
    sa.Column('bus_type', sa.String(length=50), nullable=False),
    sa.Column('interface_type', sa.String(length=50), nullable=False),
    sa.Column('size_bytes', sa.BigInteger(), nullable=False),
    sa.Column('partition_count', sa.Integer(), nullable=False),
    sa.Column('health_status', sa.String(length=50), nullable=False),
    sa.Column('operational_status', sa.String(length=50), nullable=False),
    sa.Column('is_boot_disk', sa.Boolean(), nullable=False),
    sa.Column('is_system_disk', sa.Boolean(), nullable=False),
    sa.Column('is_removable', sa.Boolean(), nullable=False),
    sa.Column('is_virtual', sa.Boolean(), nullable=False),
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
    op.create_index(op.f('ix_physical_disk_inventory_endpoint_id'), 'physical_disk_inventory', ['endpoint_id'], unique=False)
    op.create_index(op.f('ix_physical_disk_inventory_id'), 'physical_disk_inventory', ['id'], unique=False)
    op.create_index(op.f('ix_physical_disk_inventory_serial_number'), 'physical_disk_inventory', ['serial_number'], unique=False)

    op.create_table('logical_volume_inventory',
    sa.Column('disk_id', sa.Uuid(), nullable=False),
    sa.Column('drive_letter', sa.String(length=10), nullable=False),
    sa.Column('volume_name', sa.String(length=255), nullable=False),
    sa.Column('volume_guid', sa.String(length=100), nullable=False),
    sa.Column('file_system', sa.String(length=50), nullable=False),
    sa.Column('label', sa.String(length=255), nullable=False),
    sa.Column('capacity_bytes', sa.BigInteger(), nullable=False),
    sa.Column('free_space_bytes', sa.BigInteger(), nullable=False),
    sa.Column('used_space_bytes', sa.BigInteger(), nullable=False),
    sa.Column('compression_enabled', sa.Boolean(), nullable=False),
    sa.Column('bitlocker_status', sa.String(length=100), nullable=False),
    sa.Column('volume_type', sa.String(length=100), nullable=False),
    sa.Column('is_boot_volume', sa.Boolean(), nullable=False),
    sa.Column('is_system_volume', sa.Boolean(), nullable=False),
    sa.Column('shadow_copy_support', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['disk_id'], ['physical_disk_inventory.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logical_volume_inventory_disk_id'), 'logical_volume_inventory', ['disk_id'], unique=False)
    op.create_index(op.f('ix_logical_volume_inventory_drive_letter'), 'logical_volume_inventory', ['drive_letter'], unique=False)
    op.create_index(op.f('ix_logical_volume_inventory_id'), 'logical_volume_inventory', ['id'], unique=False)
    op.create_index(op.f('ix_logical_volume_inventory_volume_guid'), 'logical_volume_inventory', ['volume_guid'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_logical_volume_inventory_volume_guid'), table_name='logical_volume_inventory')
    op.drop_index(op.f('ix_logical_volume_inventory_id'), table_name='logical_volume_inventory')
    op.drop_index(op.f('ix_logical_volume_inventory_drive_letter'), table_name='logical_volume_inventory')
    op.drop_index(op.f('ix_logical_volume_inventory_disk_id'), table_name='logical_volume_inventory')
    op.drop_table('logical_volume_inventory')
    
    op.drop_index(op.f('ix_physical_disk_inventory_serial_number'), table_name='physical_disk_inventory')
    op.drop_index(op.f('ix_physical_disk_inventory_id'), table_name='physical_disk_inventory')
    op.drop_index(op.f('ix_physical_disk_inventory_endpoint_id'), table_name='physical_disk_inventory')
    op.drop_table('physical_disk_inventory')
