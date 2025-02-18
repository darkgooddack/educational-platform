"""add_field_status_in_tests

Revision ID: 86c772de072c
Revises: 5b8e7a7306b3
Create Date: 2025-02-18 19:01:32.186034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86c772de072c'
down_revision: Union[str, None] = '5b8e7a7306b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Сначала создаем тип enum
    op.execute("CREATE TYPE teststatus AS ENUM ('DRAFT', 'PUBLISHED', 'ARCHIVED')")
    # Затем добавляем колонку status в таблицу tests
    op.add_column('tests',
        sa.Column(
            'status',
            sa.Enum('DRAFT', 'PUBLISHED', 'ARCHIVED', name='teststatus'),
            nullable=False,
            server_default='DRAFT'
        )
    )


def downgrade() -> None:
    op.drop_column('tests', 'status')
    op.execute("DROP TYPE teststatus")