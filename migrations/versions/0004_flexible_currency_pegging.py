"""Convert currency pegging to flexible system

Revision ID: 0004_flexible_currency_pegging
Revises: 0003_default_currencies
Create Date: 2025-09-27 05:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '0004_flexible_currency_pegging'
down_revision: Union[str, None] = '0003_default_currencies'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert currency pegging from gold-based to flexible system."""
    
    connection = op.get_bind()
    
    # Get current gold price (approximate $2000/oz)
    gold_price_usd = 2000.0
    
    # Create new table with the flexible pegging structure
    op.create_table('currencies_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('peg_type', sa.Enum('CURRENCY', 'METAL', 'MATERIAL', name='pegtype'), nullable=False),
        sa.Column('peg_target', sa.String(), nullable=False),
        sa.Column('base_unit_value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_currencies_new_id', 'currencies_new', ['id'])
    op.create_index('ix_currencies_new_name', 'currencies_new', ['name'], unique=True)
    
    # Copy data from old table to new table with conversions
    connection.execute(text("""
        INSERT INTO currencies_new (id, name, peg_type, peg_target, base_unit_value, created_at, updated_at)
        SELECT 
            id,
            name,
            'CURRENCY' as peg_type,
            'USD' as peg_target,
            CASE 
                WHEN name = 'USD' THEN 1.0
                WHEN name = 'Euro' THEN base_unit_value_oz_gold * :gold_price * 0.92  -- EUR ~0.92 USD
                WHEN name = 'British Pound' THEN base_unit_value_oz_gold * :gold_price * 1.26  -- GBP ~1.26 USD
                WHEN name = 'Japanese Yen' THEN base_unit_value_oz_gold * :gold_price * 149.0  -- JPY ~149 per USD
                ELSE base_unit_value_oz_gold * :gold_price
            END as base_unit_value,
            created_at,
            updated_at
        FROM currencies
    """), {"gold_price": gold_price_usd})
    
    # Drop old table and rename new table
    op.drop_table('currencies')
    op.rename_table('currencies_new', 'currencies')


def downgrade() -> None:
    """Revert to gold-based pegging system."""
    
    connection = op.get_bind()
    gold_price_usd = 2000.0
    
    # Create old table structure
    op.create_table('currencies_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('base_unit_value_oz_gold', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_currencies_old_id', 'currencies_old', ['id'])
    op.create_index('ix_currencies_old_name', 'currencies_old', ['name'], unique=True)
    
    # Copy data back with conversion
    connection.execute(text("""
        INSERT INTO currencies_old (id, name, base_unit_value_oz_gold, created_at, updated_at)
        SELECT 
            id,
            name,
            CASE 
                WHEN peg_type = 'CURRENCY' AND peg_target = 'USD' THEN base_unit_value / :gold_price
                ELSE base_unit_value / :gold_price
            END as base_unit_value_oz_gold,
            created_at,
            updated_at
        FROM currencies
    """), {"gold_price": gold_price_usd})
    
    # Drop new table and rename old table
    op.drop_table('currencies')
    op.rename_table('currencies_old', 'currencies')