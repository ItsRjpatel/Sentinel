"""Add network inventory table

Revision ID: 4bb61beca30b
Revises: 4bb61beca30a
Create Date: 2026-07-30 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bb61beca30b'
down_revision: Union[str, Sequence[str], None] = '4bb61beca30a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('network_adapter_inventory',
    sa.Column('endpoint_id', sa.Uuid(), nullable=False),
    sa.Column('hostname', sa.String(length=255), nullable=False),
    sa.Column('domain_workgroup', sa.String(length=255), nullable=False),
    sa.Column('adapter_name', sa.String(length=255), nullable=False),
    sa.Column('adapter_description', sa.String(length=255), nullable=False),
    sa.Column('interface_guid', sa.String(length=100), nullable=False),
    sa.Column('mac_address', sa.String(length=100), nullable=True),
    sa.Column('ipv4', sa.String(length=100), nullable=False),
    sa.Column('ipv6', sa.String(length=200), nullable=False),
    sa.Column('subnet_mask', sa.String(length=100), nullable=False),
    sa.Column('gateway', sa.String(length=100), nullable=False),
    sa.Column('dns_servers', sa.String(length=500), nullable=False),
    sa.Column('dhcp_enabled', sa.Boolean(), nullable=False),
    sa.Column('dhcp_server', sa.String(length=100), nullable=False),
    sa.Column('lease_obtained', sa.String(length=100), nullable=False),
    sa.Column('lease_expires', sa.String(length=100), nullable=False),
    sa.Column('interface_speed', sa.BigInteger(), nullable=False),
    sa.Column('interface_type', sa.String(length=100), nullable=False),
    sa.Column('operational_status', sa.String(length=50), nullable=False),
    sa.Column('is_physical', sa.Boolean(), nullable=False),
    sa.Column('connection_type', sa.String(length=50), nullable=False),
    sa.Column('is_vpn', sa.Boolean(), nullable=False),
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
    op.create_index(op.f('ix_network_adapter_inventory_endpoint_id'), 'network_adapter_inventory', ['endpoint_id'], unique=False)
    op.create_index(op.f('ix_network_adapter_inventory_interface_guid'), 'network_adapter_inventory', ['interface_guid'], unique=False)
    op.create_index(op.f('ix_network_adapter_inventory_mac_address'), 'network_adapter_inventory', ['mac_address'], unique=False)
    op.create_index(op.f('ix_network_adapter_inventory_ipv4'), 'network_adapter_inventory', ['ipv4'], unique=False)
    op.create_index(op.f('ix_network_adapter_inventory_id'), 'network_adapter_inventory', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_network_adapter_inventory_id'), table_name='network_adapter_inventory')
    op.drop_index(op.f('ix_network_adapter_inventory_ipv4'), table_name='network_adapter_inventory')
    op.drop_index(op.f('ix_network_adapter_inventory_mac_address'), table_name='network_adapter_inventory')
    op.drop_index(op.f('ix_network_adapter_inventory_interface_guid'), table_name='network_adapter_inventory')
    op.drop_index(op.f('ix_network_adapter_inventory_endpoint_id'), table_name='network_adapter_inventory')
    op.drop_table('network_adapter_inventory')
