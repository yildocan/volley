"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-12-19 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("gender", sa.String(length=1), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weekly_recurrence", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "votes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("voter_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.UniqueConstraint("event_id", "voter_id", "target_user_id", name="uq_vote"),
    )
    op.create_index("ix_votes_event_id", "votes", ["event_id"])
    op.create_index("ix_votes_voter_id", "votes", ["voter_id"])
    op.create_index("ix_votes_target_user_id", "votes", ["target_user_id"])


def downgrade() -> None:
    op.drop_index("ix_votes_target_user_id", table_name="votes")
    op.drop_index("ix_votes_voter_id", table_name="votes")
    op.drop_index("ix_votes_event_id", table_name="votes")
    op.drop_table("votes")
    op.drop_table("events")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
