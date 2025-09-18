"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('players',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('gemstones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('value_per_carat_oz_gold', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('player_gemstones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id', ondelete='CASCADE')),
        sa.Column('gemstone_id', sa.Integer(), sa.ForeignKey('gemstones.id', ondelete='CASCADE')),
        sa.Column('carats', sa.Float(), default=0.0),
        sa.Column('appraised_value_oz_gold', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('currencies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('base_unit_value_oz_gold', sa.Float(), default=0.0),
    )
    op.create_table('currency_denominations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('currency_id', sa.Integer(), sa.ForeignKey('currencies.id', ondelete='CASCADE')),
        sa.Column('name', sa.String()),
        sa.Column('value_in_base_units', sa.Float(), default=0.0),
    )
    op.create_table('gm_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exchange_fee_percent', sa.Float(), default=0.0),
        sa.Column('interest_rate_percent', sa.Float(), default=0.0),
        sa.Column('growth_factor_percent', sa.Float(), default=0.0),
        sa.Column('hide_dollar_from_players', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('inbox_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('type', sa.String()),
        sa.Column('status', sa.String()),
        sa.Column('payload', sa.JSON()),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('metal_price_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('metal', sa.String(), index=True),
        sa.Column('price_per_ounce_gold', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('art_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('description', sa.String(), default=''),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id', ondelete='SET NULL'), nullable=True),
        sa.Column('appraised_value_oz_gold', sa.Float(), default=0.0),
        sa.Column('pending_appraisal', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('real_estate_properties',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('location', sa.String(), default=''),
        sa.Column('description', sa.String(), default=''),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id', ondelete='SET NULL'), nullable=True),
        sa.Column('appraised_value_oz_gold', sa.Float(), default=0.0),
        sa.Column('income_per_session_oz_gold', sa.Float(), default=0.0),
        sa.Column('pending_appraisal', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('businesses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('description', sa.String(), default=''),
        sa.Column('principle_activity', sa.String(), default=''),
        sa.Column('net_worth_oz_gold', sa.Float(), default=0.0),
        sa.Column('income_per_session_oz_gold', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('business_investors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.Integer(), sa.ForeignKey('businesses.id', ondelete='CASCADE')),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id', ondelete='CASCADE')),
        sa.Column('equity_percent', sa.Float(), default=0.0),
        sa.Column('invested_oz_gold', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

def downgrade():
    for table in [
        'business_investors','businesses','real_estate_properties','art_items','metal_price_history','inbox_messages',
        'gm_settings','currency_denominations','currencies','player_gemstones','gemstones','players']:
        op.drop_table(table)
