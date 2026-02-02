"""Add category system

Revision ID: 004
Revises: 003
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create category table
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=True)
    op.create_index(op.f('ix_category_slug'), 'category', ['slug'], unique=True)
    
    # Create category_tag table
    op.create_table(
        'category_tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_id', 'slug', name='uq_category_tag_category_slug')
    )
    op.create_index(op.f('ix_category_tag_category_id'), 'category_tag', ['category_id'], unique=False)
    op.create_index(op.f('ix_category_tag_name'), 'category_tag', ['name'], unique=False)
    op.create_index(op.f('ix_category_tag_slug'), 'category_tag', ['slug'], unique=False)
    
    # Create subreddit_category_tag table (many-to-many)
    op.create_table(
        'subreddit_category_tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subreddit_id', sa.Integer(), nullable=False),
        sa.Column('category_tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True, server_default='manual'),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['subreddit_id'], ['subreddit.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_tag_id'], ['category_tag.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subreddit_id', 'category_tag_id', name='uq_subreddit_category_tag')
    )
    op.create_index(op.f('ix_subreddit_category_tag_subreddit_id'), 'subreddit_category_tag', ['subreddit_id'], unique=False)
    op.create_index(op.f('ix_subreddit_category_tag_category_tag_id'), 'subreddit_category_tag', ['category_tag_id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_subreddit_category_tag_category_tag_id'), table_name='subreddit_category_tag')
    op.drop_index(op.f('ix_subreddit_category_tag_subreddit_id'), table_name='subreddit_category_tag')
    op.drop_table('subreddit_category_tag')
    
    op.drop_index(op.f('ix_category_tag_slug'), table_name='category_tag')
    op.drop_index(op.f('ix_category_tag_name'), table_name='category_tag')
    op.drop_index(op.f('ix_category_tag_category_id'), table_name='category_tag')
    op.drop_table('category_tag')
    
    op.drop_index(op.f('ix_category_slug'), table_name='category')
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.drop_table('category')
