"""Add account locking fields to User

Revision ID: 5278bf03f271
Revises: 
Create Date: 2026-07-29 13:29:36.496627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5278bf03f271'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_failed_login', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'last_failed_login')
    op.drop_column('users', 'failed_login_attempts')
