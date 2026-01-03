"""add_audit_logs

Revision ID: 002_audit_logs
Revises: 001_rbac
Create Date: 2026-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_audit_logs'
down_revision: Union[str, Sequence[str], None] = '001_rbac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_logs table."""
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('target_user_id', sa.UUID(), nullable=True),
        sa.Column('role_id', sa.UUID(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_action_entity', 'audit_logs', ['action', 'entity_type'], unique=False)
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)
    op.create_index('idx_audit_logs_entity_type', 'audit_logs', ['entity_type'], unique=False)
    op.create_index('idx_audit_logs_role_id', 'audit_logs', ['role_id'], unique=False)
    op.create_index('idx_audit_logs_target_user_id', 'audit_logs', ['target_user_id'], unique=False)
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('idx_audit_logs_user_target', 'audit_logs', ['user_id', 'target_user_id'], unique=False)


def downgrade() -> None:
    """Drop audit_logs table."""
    op.drop_index('idx_audit_logs_user_target', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('idx_audit_logs_target_user_id', table_name='audit_logs')
    op.drop_index('idx_audit_logs_role_id', table_name='audit_logs')
    op.drop_index('idx_audit_logs_entity_type', table_name='audit_logs')
    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action_entity', table_name='audit_logs')
    op.drop_table('audit_logs')
