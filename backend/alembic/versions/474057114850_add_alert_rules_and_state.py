"""add_alert_rules_and_state

Revision ID: 474057114850
Revises: 926c11bab7b4
Create Date: 2026-08-09 02:46:22.934608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '474057114850'
down_revision: Union[str, Sequence[str], None] = '900000000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('alert_type', sa.String(length=100), server_default='custom', nullable=False))


def downgrade() -> None:
    op.drop_column('alerts', 'alert_type')
