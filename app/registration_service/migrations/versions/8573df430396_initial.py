"""update_user_migration

Revision ID: 8573df430396
Revises: 
Create Date: 2024-12-05 13:57:00.650418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8573df430396'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users_register',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('phone_number', sa.String, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('role', sa.Enum('student', 'teacher', 'professor', name='user_roles'), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('users_register')
    op.execute("DROP TYPE user_roles")