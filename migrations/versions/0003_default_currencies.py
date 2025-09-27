"""Default currencies

Revision ID: 0003_default_currencies
Revises: 0002_materials
Create Date: 2025-09-27 05:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '0003_default_currencies'
down_revision: Union[str, None] = '0002_materials'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add default currencies with their gold peg values."""
    
    # Create currencies table connection
    connection = op.get_bind()
    
    # Default currencies with approximate gold peg values
    # Assuming gold is around $2000/oz, these are rough estimates
    default_currencies = [
        {
            'name': 'US Dollar',
            'base_unit_value_oz_gold': 0.0005,  # $1 USD = 0.0005 oz gold (if gold = $2000/oz)
            'denominations': [
                {'name': 'Penny', 'value': 0.01},
                {'name': 'Nickel', 'value': 0.05},
                {'name': 'Dime', 'value': 0.10},
                {'name': 'Quarter', 'value': 0.25},
                {'name': 'Dollar', 'value': 1.0},
                {'name': 'Five Dollar Bill', 'value': 5.0},
                {'name': 'Ten Dollar Bill', 'value': 10.0},
                {'name': 'Twenty Dollar Bill', 'value': 20.0},
                {'name': 'Fifty Dollar Bill', 'value': 50.0},
                {'name': 'Hundred Dollar Bill', 'value': 100.0}
            ]
        },
        {
            'name': 'Euro',
            'base_unit_value_oz_gold': 0.00054,  # €1 = 0.00054 oz gold (EUR slightly stronger than USD)
            'denominations': [
                {'name': '1 Cent', 'value': 0.01},
                {'name': '2 Cent', 'value': 0.02},
                {'name': '5 Cent', 'value': 0.05},
                {'name': '10 Cent', 'value': 0.10},
                {'name': '20 Cent', 'value': 0.20},
                {'name': '50 Cent', 'value': 0.50},
                {'name': '1 Euro', 'value': 1.0},
                {'name': '2 Euro', 'value': 2.0},
                {'name': '5 Euro Note', 'value': 5.0},
                {'name': '10 Euro Note', 'value': 10.0},
                {'name': '20 Euro Note', 'value': 20.0},
                {'name': '50 Euro Note', 'value': 50.0},
                {'name': '100 Euro Note', 'value': 100.0}
            ]
        },
        {
            'name': 'British Pound',
            'base_unit_value_oz_gold': 0.00063,  # £1 = 0.00063 oz gold (GBP stronger than USD)
            'denominations': [
                {'name': '1 Penny', 'value': 0.01},
                {'name': '2 Pence', 'value': 0.02},
                {'name': '5 Pence', 'value': 0.05},
                {'name': '10 Pence', 'value': 0.10},
                {'name': '20 Pence', 'value': 0.20},
                {'name': '50 Pence', 'value': 0.50},
                {'name': '1 Pound', 'value': 1.0},
                {'name': '2 Pound', 'value': 2.0},
                {'name': '5 Pound Note', 'value': 5.0},
                {'name': '10 Pound Note', 'value': 10.0},
                {'name': '20 Pound Note', 'value': 20.0},
                {'name': '50 Pound Note', 'value': 50.0}
            ]
        },
        {
            'name': 'Japanese Yen',
            'base_unit_value_oz_gold': 0.0000033,  # ¥1 = 0.0000033 oz gold (weak currency, many units)
            'denominations': [
                {'name': '1 Yen', 'value': 1.0},
                {'name': '5 Yen', 'value': 5.0},
                {'name': '10 Yen', 'value': 10.0},
                {'name': '50 Yen', 'value': 50.0},
                {'name': '100 Yen', 'value': 100.0},
                {'name': '500 Yen', 'value': 500.0},
                {'name': '1000 Yen Note', 'value': 1000.0},
                {'name': '5000 Yen Note', 'value': 5000.0},
                {'name': '10000 Yen Note', 'value': 10000.0}
            ]
        }
    ]
    
    # Insert currencies and their denominations
    for currency_data in default_currencies:
        # Check if currency already exists
        result = connection.execute(
            text("SELECT id FROM currencies WHERE name = :name"),
            {"name": currency_data['name']}
        )
        existing = result.fetchone()
        
        if not existing:
            # Insert currency
            result = connection.execute(
                text("""
                    INSERT INTO currencies (name, base_unit_value_oz_gold, created_at, updated_at) 
                    VALUES (:name, :base_unit_value_oz_gold, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """),
                {
                    "name": currency_data['name'],
                    "base_unit_value_oz_gold": currency_data['base_unit_value_oz_gold']
                }
            )
            row = result.fetchone()
            if row:
                currency_id = row[0]
            else:
                continue  # Skip if insertion failed
            
            # Insert denominations
            for denom in currency_data['denominations']:
                connection.execute(
                    text("""
                        INSERT INTO currency_denominations (currency_id, name, value_in_base_units)
                        VALUES (:currency_id, :name, :value_in_base_units)
                    """),
                    {
                        "currency_id": currency_id,
                        "name": denom['name'],
                        "value_in_base_units": denom['value']
                    }
                )


def downgrade() -> None:
    """Remove default currencies."""
    connection = op.get_bind()
    
    # Remove the default currencies we added
    default_currency_names = ['US Dollar', 'Euro', 'British Pound', 'Japanese Yen']
    
    for name in default_currency_names:
        # Delete denominations first (due to foreign key constraint)
        connection.execute(
            text("""
                DELETE FROM currency_denominations 
                WHERE currency_id IN (SELECT id FROM currencies WHERE name = :name)
            """),
            {"name": name}
        )
        
        # Delete currency
        connection.execute(
            text("DELETE FROM currencies WHERE name = :name"),
            {"name": name}
        )