"""Prune currencies to USD and Gold

Revision ID: 0005_prune_currencies
Revises: 0004_flexible_currency_pegging
Create Date: 2025-09-27 06:19:00

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "0005_prune_currencies"
down_revision: Union[str, None] = "0004_flexible_currency_pegging"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        text(
            """
            UPDATE currencies
            SET name = 'USD', updated_at = CURRENT_TIMESTAMP
            WHERE name = 'US Dollar'
            """
        )
    )

    connection.execute(
        text(
            """
            UPDATE currencies
            SET peg_type = 'CURRENCY', peg_target = 'USD', base_unit_value = 1.0, updated_at = CURRENT_TIMESTAMP
            WHERE name = 'USD'
            """
        )
    )

    gold_row = connection.execute(
        text("SELECT id FROM currencies WHERE name = 'Gold'")
    ).fetchone()

    if gold_row is None:
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
    else:
        connection.execute(
            text(
                """
                UPDATE currencies
                SET peg_type = 'METAL', peg_target = 'Gold', base_unit_value = 1.0, updated_at = CURRENT_TIMESTAMP
                WHERE id = :gold_id
                """
            ),
            {"gold_id": gold_row[0]},
        )

    connection.execute(
        text(
            """
            DELETE FROM currency_denominations
            WHERE currency_id IN (
                SELECT id FROM currencies WHERE name NOT IN ('USD', 'Gold')
            )
            """
        )
    )

    connection.execute(
        text(
            """
            DELETE FROM currencies
            WHERE name NOT IN ('USD', 'Gold')
            """
        )
    )


def downgrade() -> None:
    connection = op.get_bind()

    gold_row = connection.execute(text("SELECT id FROM currencies WHERE name = 'Gold'"))
    gold_id_row = gold_row.fetchone()
    if gold_id_row is not None:
        connection.execute(
            text("DELETE FROM currency_denominations WHERE currency_id = :gold_id"),
            {"gold_id": gold_id_row[0]},
        )
        connection.execute(
            text("DELETE FROM currencies WHERE id = :gold_id"),
            {"gold_id": gold_id_row[0]},
        )

    connection.execute(
        text(
            """
            UPDATE currencies
            SET name = 'US Dollar', peg_type = 'CURRENCY', peg_target = 'USD', base_unit_value = 1.0, updated_at = CURRENT_TIMESTAMP
            WHERE name = 'USD'
            """
        )
    )

    default_currencies = [
        {
            "name": "Euro",
            "base_unit_value": 0.9936,
            "denominations": [
                ("1 Cent", 0.01),
                ("2 Cent", 0.02),
                ("5 Cent", 0.05),
                ("10 Cent", 0.10),
                ("20 Cent", 0.20),
                ("50 Cent", 0.50),
                ("1 Euro", 1.0),
                ("2 Euro", 2.0),
                ("5 Euro Note", 5.0),
                ("10 Euro Note", 10.0),
                ("20 Euro Note", 20.0),
                ("50 Euro Note", 50.0),
                ("100 Euro Note", 100.0),
            ],
        },
        {
            "name": "British Pound",
            "base_unit_value": 1.5876,
            "denominations": [
                ("1 Penny", 0.01),
                ("2 Pence", 0.02),
                ("5 Pence", 0.05),
                ("10 Pence", 0.10),
                ("20 Pence", 0.20),
                ("50 Pence", 0.50),
                ("1 Pound", 1.0),
                ("2 Pound", 2.0),
                ("5 Pound Note", 5.0),
                ("10 Pound Note", 10.0),
                ("20 Pound Note", 20.0),
                ("50 Pound Note", 50.0),
            ],
        },
        {
            "name": "Japanese Yen",
            "base_unit_value": 0.9834,
            "denominations": [
                ("1 Yen", 1.0),
                ("5 Yen", 5.0),
                ("10 Yen", 10.0),
                ("50 Yen", 50.0),
                ("100 Yen", 100.0),
                ("500 Yen", 500.0),
                ("1000 Yen Note", 1000.0),
                ("5000 Yen Note", 5000.0),
                ("10000 Yen Note", 10000.0),
            ],
        },
    ]

    for currency_data in default_currencies:
        existing = connection.execute(
            text("SELECT id FROM currencies WHERE name = :name"),
            {"name": currency_data["name"]},
        ).fetchone()

        if existing is None:
            result = connection.execute(
                text(
                    """
                    INSERT INTO currencies (name, peg_type, peg_target, base_unit_value, created_at, updated_at)
                    VALUES (:name, 'CURRENCY', 'USD', :base_unit_value, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                    """
                ),
                {
                    "name": currency_data["name"],
                    "base_unit_value": currency_data["base_unit_value"],
                },
            )
            currency_id = result.scalar()
        else:
            currency_id = existing[0]
            connection.execute(
                text(
                    """
                    UPDATE currencies
                    SET peg_type = 'CURRENCY', peg_target = 'USD', base_unit_value = :base_unit_value, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :currency_id
                    """
                ),
                {
                    "currency_id": currency_id,
                    "base_unit_value": currency_data["base_unit_value"],
                },
            )
            connection.execute(
                text("DELETE FROM currency_denominations WHERE currency_id = :currency_id"),
                {"currency_id": currency_id},
            )

        for denom_name, denom_value in currency_data["denominations"]:
            connection.execute(
                text(
                    """
                    INSERT INTO currency_denominations (currency_id, name, value_in_base_units)
                    VALUES (:currency_id, :name, :value_in_base_units)
                    """
                ),
                {
                    "currency_id": currency_id,
                    "name": denom_name,
                    "value_in_base_units": denom_value,
                },
            )
