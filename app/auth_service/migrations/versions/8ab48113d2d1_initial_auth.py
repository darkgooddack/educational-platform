"""initial_auth

Revision ID: 8ab48113d2d1
Revises: 
Create Date: 2024-09-22 14:30:05.490085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ab48113d2d1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users_auth',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('password', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, default=False),
    )
    op.create_index('ix_users_auth_is_active', 'users_auth', ['is_active'])

    op.create_table(
        'user_tokens',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users_auth.id'), nullable=False),
        sa.Column('access_token', sa.String(250), nullable=True),
        sa.Column('refresh_token', sa.String(250), nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_user_tokens_access_token', 'user_tokens', ['access_token'])
    op.create_index('ix_user_tokens_refresh_token', 'user_tokens', ['refresh_token'])
    op.create_index('ix_user_tokens_user_id', 'user_tokens', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_tokens_user_id', table_name='user_tokens')
    op.drop_index('ix_user_tokens_refresh_token', table_name='user_tokens')
    op.drop_index('ix_user_tokens_access_token', table_name='user_tokens')
    op.drop_table('user_tokens')

    op.drop_index('ix_users_auth_is_active', table_name='users_auth')
    op.drop_table('users_auth')
