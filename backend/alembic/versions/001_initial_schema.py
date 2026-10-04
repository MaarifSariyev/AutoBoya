"""Initial database schema with core entities, constraints and indexes

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-25 20:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_superuser', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # 2. Vehicle Brands
    op.create_table(
        'vehicle_brands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_vehicle_brands_name', 'vehicle_brands', ['name'])

    # 3. Vehicle Models
    op.create_table(
        'vehicle_models',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('year_from', sa.Integer(), nullable=True),
        sa.Column('year_to', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['vehicle_brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('brand_id', 'name', name='uq_brand_model_name')
    )
    op.create_index('ix_vehicle_models_brand_id', 'vehicle_models', ['brand_id'])
    op.create_index('ix_vehicle_models_name', 'vehicle_models', ['name'])

    # 4. Component Library
    op.create_table(
        'component_library',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('unit', sa.String(length=20), server_default='g', nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_component_library_code', 'component_library', ['code'])
    op.create_index('ix_component_library_name', 'component_library', ['name'])

    # 5. Colors table
    op.create_table(
        'colors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('color_code', sa.String(length=50), nullable=False),
        sa.Column('color_name', sa.String(length=100), nullable=False),
        sa.Column('color_type', sa.String(length=30), server_default='Metallic', nullable=False),
        sa.Column('paint_system', sa.String(length=50), server_default='Basecoat', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['vehicle_brands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['vehicle_models.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('brand_id', 'color_code', 'paint_system', name='uq_brand_color_system')
    )
    op.create_index('ix_colors_brand_id', 'colors', ['brand_id'])
    op.create_index('ix_colors_model_id', 'colors', ['model_id'])
    op.create_index('ix_colors_color_code', 'colors', ['color_code'])
    op.create_index('ix_colors_color_name', 'colors', ['color_name'])
    op.create_index('ix_colors_paint_system', 'colors', ['paint_system'])

    # 6. Formulas table
    op.create_table(
        'formulas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('color_id', sa.Integer(), nullable=False),
        sa.Column('formula_name', sa.String(length=150), nullable=False),
        sa.Column('variant_name', sa.String(length=50), server_default='Standard', nullable=False),
        sa.Column('paint_system', sa.String(length=50), server_default='Basecoat', nullable=False),
        sa.Column('base_total_amount', sa.Numeric(precision=12, scale=4), server_default='1000.0000', nullable=False),
        sa.Column('unit', sa.String(length=20), server_default='g', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='DRAFT', nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('source_type', sa.String(length=30), server_default='EXPERT_CREATED', nullable=False),
        sa.Column('expert_notes', sa.Text(), nullable=True),
        sa.Column('preparation_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=150), nullable=True),
        sa.Column('verified_by', sa.String(length=150), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['color_id'], ['colors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_formulas_color_id', 'formulas', ['color_id'])
    op.create_index('ix_formulas_status', 'formulas', ['status'])
    op.create_index('ix_formulas_variant_name', 'formulas', ['variant_name'])

    # 7. Formula Components table
    op.create_table(
        'formula_components',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('formula_id', sa.Integer(), nullable=False),
        sa.Column('component_code', sa.String(length=50), nullable=False),
        sa.Column('component_name', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('unit', sa.String(length=20), server_default='g', nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['formula_id'], ['formulas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_formula_components_formula_id', 'formula_components', ['formula_id'])
    op.create_index('ix_formula_components_component_code', 'formula_components', ['component_code'])

    # 8. Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_email', sa.String(length=150), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=50), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_user_email', 'audit_logs', ['user_email'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('formula_components')
    op.drop_table('formulas')
    op.drop_table('colors')
    op.drop_table('component_library')
    op.drop_table('vehicle_models')
    op.drop_table('vehicle_brands')
    op.drop_table('users')
