"""add roles for users

Revision ID: 4f5486baceeb
Revises: 807472376755
Create Date: 2025-01-29 18:25:52.249699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f5486baceeb'
down_revision: Union[str, None] = '807472376755'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'MANAGER'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("""
        CREATE TYPE userrole_new AS ENUM ('ADMIN', 'MODERATOR', 'USER');
        ALTER TABLE users ALTER COLUMN role TYPE userrole_new USING role::text::userrole_new;
        DROP TYPE userrole;
        ALTER TYPE userrole_new RENAME TO userrole;
    """)
    # ### end Alembic commands ###
