"""Add token tracking to conversations and messages

Revision ID: a0f6d3dc34bf
Revises: c2a7fd48d7e3
Create Date: 2025-10-09 10:56:44.221355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0f6d3dc34bf'
down_revision: Union[str, Sequence[str], None] = 'c2a7fd48d7e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add token tracking fields to conversations table
    op.add_column('conversations', sa.Column('context_window_size', sa.Integer(), nullable=False, server_default='2048'))
    op.add_column('conversations', sa.Column('current_token_count', sa.Integer(), nullable=False, server_default='0'))

    # Add token count field to messages table
    op.add_column('messages', sa.Column('token_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove token tracking fields
    op.drop_column('messages', 'token_count')
    op.drop_column('conversations', 'current_token_count')
    op.drop_column('conversations', 'context_window_size')
