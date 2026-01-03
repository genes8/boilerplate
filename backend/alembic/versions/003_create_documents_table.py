"""create_documents_table

Revision ID: 003_documents
Revises: 002_audit_logs
Create Date: 2026-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_documents'
down_revision: Union[str, Sequence[str], None] = '002_audit_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create documents table with full-text search support."""
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Basic indexes
    op.create_index('idx_documents_title', 'documents', ['title'], unique=False)
    op.create_index('idx_documents_owner_id', 'documents', ['owner_id'], unique=False)
    op.create_index('idx_documents_created_at', 'documents', ['created_at'], unique=False)
    
    # GIN index for full-text search on search_vector
    op.create_index(
        'idx_documents_search_vector',
        'documents',
        ['search_vector'],
        unique=False,
        postgresql_using='gin'
    )
    
    # Trigram indexes for fuzzy search
    op.create_index(
        'idx_documents_title_trgm',
        'documents',
        ['title'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'title': 'gin_trgm_ops'}
    )
    op.create_index(
        'idx_documents_content_trgm',
        'documents',
        ['content'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'content': 'gin_trgm_ops'}
    )
    
    # Create trigger function to auto-update search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to call the function on insert/update
    op.execute("""
        CREATE TRIGGER documents_search_vector_trigger
        BEFORE INSERT OR UPDATE OF title, content ON documents
        FOR EACH ROW
        EXECUTE FUNCTION documents_search_vector_update();
    """)


def downgrade() -> None:
    """Drop documents table and related objects."""
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS documents_search_vector_trigger ON documents;")
    
    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS documents_search_vector_update();")
    
    # Drop indexes
    op.drop_index('idx_documents_content_trgm', table_name='documents')
    op.drop_index('idx_documents_title_trgm', table_name='documents')
    op.drop_index('idx_documents_search_vector', table_name='documents')
    op.drop_index('idx_documents_created_at', table_name='documents')
    op.drop_index('idx_documents_owner_id', table_name='documents')
    op.drop_index('idx_documents_title', table_name='documents')
    
    # Drop table
    op.drop_table('documents')
