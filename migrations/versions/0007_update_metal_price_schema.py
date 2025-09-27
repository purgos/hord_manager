"""Align metal price history schema with ORM model

Revision ID: 0007_update_metal_price_schema
Revises: 0006_remove_gold_currency
Create Date: 2025-09-27
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0007_update_metal_price_schema"
down_revision = "0006_remove_gold_currency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE metal_price_history RENAME TO metal_price_history_old")

    op.create_table(
        "metal_price_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("metal_name", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("price_per_unit_usd", sa.Float(), nullable=False),
        sa.Column("price_per_oz_gold", sa.Float(), nullable=False),
        sa.Column("session_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index(
        "ix_metal_price_history_metal_name",
        "metal_price_history",
        ["metal_name"],
    )
    op.create_index(
        "ix_metal_price_history_session_number",
        "metal_price_history",
        ["session_number"],
    )

    op.execute(
        """
        INSERT INTO metal_price_history (
            id,
            metal_name,
            unit,
            price_per_unit_usd,
            price_per_oz_gold,
            session_number,
            created_at
        )
        SELECT
            id,
            metal,
            'oz',
            price_per_ounce_gold,
            price_per_ounce_gold,
            1,
            created_at
        FROM metal_price_history_old
        """
    )

    op.execute("DROP TABLE metal_price_history_old")


def downgrade() -> None:
    op.execute("ALTER TABLE metal_price_history RENAME TO metal_price_history_new")

    op.create_table(
        "metal_price_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("metal", sa.String(), nullable=True),
        sa.Column("price_per_ounce_gold", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index(
        "ix_metal_price_history_metal",
        "metal_price_history",
        ["metal"],
    )

    op.execute(
        """
        INSERT INTO metal_price_history (
            id,
            metal,
            price_per_ounce_gold,
            created_at
        )
        SELECT
            id,
            metal_name,
            price_per_oz_gold,
            created_at
        FROM metal_price_history_new
        """
    )

    op.execute("DROP TABLE metal_price_history_new")
