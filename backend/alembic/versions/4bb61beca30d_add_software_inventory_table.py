"""Add software inventory table

Revision ID: 4bb61beca30d
Revises: 4bb61beca30c
Create Date: 2026-07-30 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bb61beca30d'
down_revision: Union[str, Sequence[str], None] = '4bb61beca30c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('software_inventory',
    sa.Column('endpoint_id', sa.Uuid(), nullable=False),
    sa.Column('application_name', sa.String(length=255), nullable=False),
    sa.Column('publisher', sa.String(length=255), nullable=False),
    sa.Column('version', sa.String(length=100), nullable=False),
    sa.Column('install_date', sa.String(length=50), nullable=False),
    sa.Column('install_location', sa.String(length=500), nullable=False),
    sa.Column('estimated_size_kb', sa.BigInteger(), nullable=False),
    sa.Column('uninstall_string', sa.String(length=500), nullable=False),
    sa.Column('install_source', sa.String(length=500), nullable=False),
    sa.Column('architecture', sa.String(length=50), nullable=False),
    sa.Column('language', sa.String(length=50), nullable=False),
    sa.Column('product_code', sa.String(length=100), nullable=False),
    sa.Column('system_component', sa.Boolean(), nullable=False),
    sa.Column('windows_installer', sa.Boolean(), nullable=False),
    sa.Column('url_info', sa.String(length=500), nullable=False),
    sa.Column('help_link', sa.String(length=500), nullable=False),
    sa.Column('modify_path', sa.String(length=500), nullable=False),
    sa.Column('install_scope', sa.String(length=50), nullable=False),
    sa.Column('registry_key', sa.String(length=500), nullable=False),
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
    op.create_index(op.f('ix_software_inventory_application_name'), 'software_inventory', ['application_name'], unique=False)
    op.create_index(op.f('ix_software_inventory_endpoint_id'), 'software_inventory', ['endpoint_id'], unique=False)
    op.create_index(op.f('ix_software_inventory_id'), 'software_inventory', ['id'], unique=False)
    op.create_index(op.f('ix_software_inventory_publisher'), 'software_inventory', ['publisher'], unique=False)
    op.create_index(op.f('ix_software_inventory_version'), 'software_inventory', ['version'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_software_inventory_version'), table_name='software_inventory')
    op.drop_index(op.f('ix_software_inventory_publisher'), table_name='software_inventory')
    op.drop_index(op.f('ix_software_inventory_id'), table_name='software_inventory')
    op.drop_index(op.f('ix_software_inventory_endpoint_id'), table_name='software_inventory')
    op.drop_index(op.f('ix_software_inventory_application_name'), table_name='software_inventory')
    op.drop_table('software_inventory')
