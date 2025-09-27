"""add materials table

Revision ID: 0002_materials
Revises: 0001_initial
Create Date: 2025-09-27

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_materials'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade():
    # Create material_price_history table
    op.create_table('material_price_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('material_name', sa.String(), index=True),
        sa.Column('unit', sa.String()),
        sa.Column('price_per_unit_usd', sa.Float()),
        sa.Column('price_per_oz_gold', sa.Float()),
        sa.Column('session_number', sa.Integer(), index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('material_price_history')