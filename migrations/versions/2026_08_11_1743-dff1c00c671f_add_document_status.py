"""Add document status

Revision ID: dff1c00c671f
Revises: 81c7e2ece8a4
Create Date: 2026-08-11 17:43:16.358149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dff1c00c671f'
down_revision: Union[str, Sequence[str], None] = '81c7e2ece8a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server_default="COMPLETED" so existing rows get populated
    op.add_column('documents', sa.Column('status', sa.String(length=50), server_default='COMPLETED', nullable=False))
    op.add_column('documents', sa.Column('error_message', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'error_message')
    op.drop_column('documents', 'status')
