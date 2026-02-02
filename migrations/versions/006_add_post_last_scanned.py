"""add post last_scanned column

Revision ID: 006
Revises: 005
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add last_scanned column to track when posts were last processed
    # Nullable initially to allow existing posts to have NULL values
    op.add_column('post', sa.Column('last_scanned', sa.DateTime(), nullable=True))
    
    # Create an index on last_scanned for efficient queries
    op.create_index('ix_post_last_scanned', 'post', ['last_scanned'])


def downgrade():
    # Remove the index and column
    op.drop_index('ix_post_last_scanned', table_name='post')
    op.drop_column('post', 'last_scanned')
