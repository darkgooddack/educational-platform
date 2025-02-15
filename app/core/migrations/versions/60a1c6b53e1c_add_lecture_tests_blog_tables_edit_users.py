"""add_lecture_tests_blog_tables_edit_users

Revision ID: 60a1c6b53e1c
Revises: d2e08fbca18b
Create Date: 2025-02-03 19:19:30.311430

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "60a1c6b53e1c"
down_revision: Union[str, None] = "d2e08fbca18b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tags",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "themes",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["themes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lectures",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["theme_id"],
            ["themes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "posts",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PUBLISHED", "ARCHIVED", name="poststatus"),
            nullable=False,
        ),
        sa.Column("views", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lecture_content_blocks",
        sa.Column("lecture_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("TEXT", "IMAGE", "VIDEO", "AUDIO", "CODE", name="contenttype"),
            nullable=False,
        ),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("caption", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["lecture_id"],
            ["lectures.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "post_content_blocks",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("TEXT", "IMAGE", "VIDEO", "AUDIO", "CODE", name="contenttype"),
            nullable=False,
        ),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("caption", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "tag_id", "id"),
        sa.UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
    )
    op.create_table(
        "tests",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("passing_score", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("video_lecture_id", sa.Integer(), nullable=True),
        sa.Column("lecture_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lecture_id"],
            ["lectures.id"],
        ),
        sa.ForeignKeyConstraint(
            ["theme_id"],
            ["themes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["video_lecture_id"],
            ["video_lectures.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "questions",
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "type", sa.Enum("SINGLE", "MULTIPLE", name="questiontype"), nullable=False
        ),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_id"],
            ["tests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "answers",
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "users",
        sa.Column("is_online", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users", sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("video_lectures", sa.Column("theme_id", sa.Integer(), nullable=False))
    op.create_foreign_key(None, "video_lectures", "themes", ["theme_id"], ["id"])
    op.drop_column("video_lectures", "theme")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "video_lectures",
        sa.Column("theme", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "video_lectures", type_="foreignkey")
    op.drop_column("video_lectures", "theme_id")
    op.drop_column("users", "last_seen")
    op.drop_column("users", "is_online")
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("tests")
    op.drop_table("post_tags")
    op.drop_table("post_content_blocks")
    op.drop_table("lecture_content_blocks")
    op.drop_table("posts")
    op.drop_table("lectures")
    op.drop_table("themes")
    op.drop_table("tags")
    # ### end Alembic commands ###
