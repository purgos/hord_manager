"""Merge legacy branch into latest metal price schema

Revision ID: 0008_merge_metal_price_schema
Revises: 0007_update_metal_price_schema
Create Date: 2025-09-27
"""

# This migration intentionally left blank. Earlier work on metal price history
# was superseded by ``0007_update_metal_price_schema``. We keep this file as a
# no-op merge revision so Alembic sees a single head.

# revision identifiers, used by Alembic.
revision = "0008_merge_metal_price_schema"
down_revision = "0007_update_metal_price_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
