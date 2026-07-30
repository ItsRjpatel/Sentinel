"""add commands table

Revision ID: 4bb61beca310
Revises: 4bb61beca30f
Create Date: 2026-07-30 06:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4bb61beca310'
down_revision = '4bb61beca30f'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'commands',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('endpoint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('command_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_commands_endpoint_id'), 'commands', ['endpoint_id'], unique=False)
    op.create_index(op.f('ix_commands_status'), 'commands', ['status'], unique=False)
    op.create_index(op.f('ix_commands_command_type'), 'commands', ['command_type'], unique=False)
    op.create_index(op.f('ix_commands_created_at'), 'commands', ['created_at'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_commands_created_at'), table_name='commands')
    op.drop_index(op.f('ix_commands_command_type'), table_name='commands')
    op.drop_index(op.f('ix_commands_status'), table_name='commands')
    op.drop_index(op.f('ix_commands_endpoint_id'), table_name='commands')
    op.drop_table('commands')
