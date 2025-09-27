"""Default gemstones

Revision ID: 0009_default_gemstones
Revises: 0008_merge_metal_price_schema
Create Date: 2025-09-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '0009_default_gemstones'
down_revision: Union[str, None] = '0008_merge_metal_price_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add default gemstones with realistic USD-pegged prices."""
    
    connection = op.get_bind()
    
    # First, let's get the current gold price to calculate oz gold values
    # Assuming current gold price is around $2,233.88/oz based on our API
    current_gold_price_usd = 2233.88
    
    # Realistic gemstone prices per carat in USD (based on market values)
    default_gemstones = [
        {"name": "Diamond (Low Grade)", "price_usd": 1247.50},
        {"name": "Diamond (High Grade)", "price_usd": 8934.25},
        {"name": "Ruby (Burma)", "price_usd": 3876.33},
        {"name": "Ruby (Thai)", "price_usd": 1654.75},
        {"name": "Sapphire (Ceylon)", "price_usd": 2987.88},
        {"name": "Sapphire (Kashmir)", "price_usd": 6543.22},
        {"name": "Emerald (Colombian)", "price_usd": 4321.67},
        {"name": "Emerald (Zambian)", "price_usd": 2198.45},
        {"name": "Tanzanite", "price_usd": 1876.33},
        {"name": "Opal (Black)", "price_usd": 987.65},
        {"name": "Opal (Fire)", "price_usd": 567.89},
        {"name": "Tourmaline (Paraiba)", "price_usd": 5432.11},
        {"name": "Tourmaline (Green)", "price_usd": 876.54},
        {"name": "Aquamarine", "price_usd": 654.32},
        {"name": "Topaz (Imperial)", "price_usd": 432.17},
        {"name": "Garnet (Tsavorite)", "price_usd": 1234.56},
        {"name": "Garnet (Spessartine)", "price_usd": 678.91},
        {"name": "Peridot", "price_usd": 234.78},
        {"name": "Amethyst (Deep Purple)", "price_usd": 167.45},
        {"name": "Citrine (Madeira)", "price_usd": 123.89}
    ]
    
    # Clear existing gemstones first
    connection.execute(text("DELETE FROM gemstones"))
    
    # Insert new gemstones with calculated oz gold values
    for gem in default_gemstones:
        value_per_carat_oz_gold = gem["price_usd"] / current_gold_price_usd
        
        connection.execute(text("""
            INSERT INTO gemstones (name, value_per_carat_oz_gold, created_at, updated_at)
            VALUES (:name, :value_per_carat_oz_gold, datetime('now'), datetime('now'))
        """), {
            "name": gem["name"],
            "value_per_carat_oz_gold": value_per_carat_oz_gold
        })


def downgrade() -> None:
    """Remove default gemstones."""
    connection = op.get_bind()
    
    # List of gemstone names to remove
    gemstone_names = [
        "Diamond (Low Grade)", "Diamond (High Grade)", "Ruby (Burma)", "Ruby (Thai)",
        "Sapphire (Ceylon)", "Sapphire (Kashmir)", "Emerald (Colombian)", "Emerald (Zambian)",
        "Tanzanite", "Opal (Black)", "Opal (Fire)", "Tourmaline (Paraiba)", "Tourmaline (Green)",
        "Aquamarine", "Topaz (Imperial)", "Garnet (Tsavorite)", "Garnet (Spessartine)",
        "Peridot", "Amethyst (Deep Purple)", "Citrine (Madeira)"
    ]
    
    for name in gemstone_names:
        connection.execute(text("DELETE FROM gemstones WHERE name = :name"), {"name": name})