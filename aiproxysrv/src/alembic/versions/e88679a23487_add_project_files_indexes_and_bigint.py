"""add_project_files_indexes_and_bigint

Revision ID: e88679a23487
Revises: 4bdf9393c652
Create Date: 2025-11-22 13:20:45.994564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e88679a23487'
down_revision: Union[str, Sequence[str], None] = '4bdf9393c652'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    1. Add composite index on (project_id, relative_path) for faster Mirror Sync updates
    2. Change file_size_bytes from Integer to BigInteger to support files >2GB
    """
    # Add composite index for Mirror Sync update detection
    op.create_index(
        "ix_project_files_project_relative_path",
        "project_files",
        ["project_id", "relative_path"],
        unique=False,
    )

    # Upgrade file_size_bytes to BigInteger for files >2GB
    op.alter_column(
        "project_files",
        "file_size_bytes",
        type_=sa.BigInteger(),
        existing_type=sa.Integer(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop composite index
    op.drop_index("ix_project_files_project_relative_path", table_name="project_files")

    # Downgrade file_size_bytes back to Integer
    # WARNING: This will fail if any file_size_bytes values exceed Integer range (>2GB)
    op.alter_column(
        "project_files",
        "file_size_bytes",
        type_=sa.Integer(),
        existing_type=sa.BigInteger(),
        existing_nullable=True,
    )
