"""add thumbail field in videolecturemodel

Revision ID: d2e08fbca18b
Revises: 2d0ba6a0eb7e
Create Date: 2025-02-02 17:09:40.331879

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d2e08fbca18b"
down_revision: Union[str, None] = "2d0ba6a0eb7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "video_lectures", sa.Column("thumbnail_url", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("video_lectures", "thumbnail_url")
    # ### end Alembic commands ###
