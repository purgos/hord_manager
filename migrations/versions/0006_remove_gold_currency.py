"""Remove gold currency leaving only USD

Revision ID: 0006_remove_gold_currency
Revises: 0005_prune_currencies
Create Date: 2025-09-27 07:10:00

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "0006_remove_gold_currency"
down_revision: Union[str, None] = "0005_prune_currencies"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    gold_id = connection.execute(
        text("SELECT id FROM currencies WHERE name = 'Gold'")
    ).scalar()

    if gold_id is not None:
        connection.execute(
            text("DELETE FROM currency_denominations WHERE currency_id = :gold_id"),
            {"gold_id": gold_id},
        )
        connection.execute(
            text("DELETE FROM currencies WHERE id = :gold_id"),
            {"gold_id": gold_id},
        )


def downgrade() -> None:
    connection = op.get_bind()

    existing_id = connection.execute(
        text("SELECT id FROM currencies WHERE name = 'Gold'")
    ).scalar()

    if existing_id is None:
        result = connection.execute(
            text(
                """
                INSERT INTO currencies (name, peg_type, peg_target, base_unit_value, created_at, updated_at)
                VALUES ('Gold', 'METAL', 'Gold', 1.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
                """
            )
        )
        gold_id = result.scalar()
    else:
        gold_id = existing_id
        connection.execute(
            text(
                """
                UPDATE currencies
                SET peg_type = 'METAL', peg_target = 'Gold', base_unit_value = 1.0, updated_at = CURRENT_TIMESTAMP
                WHERE id = :gold_id
                """
            ),
            {"gold_id": gold_id},
        )
        connection.execute(
            text("DELETE FROM currency_denominations WHERE currency_id = :gold_id"),
            {"gold_id": gold_id},
        )

    if gold_id is not None:
        connection.execute(
            text(
                """
                INSERT INTO currency_denominations (currency_id, name, value_in_base_units)
                VALUES
                    (:gold_id, 'One Ounce Ingot', 1.0),
                    (:gold_id, 'Half Ounce Bar', 0.5),
                    (:gold_id, 'Quarter Ounce Coin', 0.25),
                    (:gold_id, 'Tenth Ounce Coin', 0.1)
                """
            ),
            {"gold_id": gold_id},
        )
