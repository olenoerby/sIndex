"""Rename public_description to description

Revision ID: 008
Revises: 007
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Rename the column from public_description to description
    op.alter_column('subreddit', 'public_description', new_column_name='description')


def downgrade():
    # Rename the column back from description to public_description
    op.alter_column('subreddit', 'description', new_column_name='public_description')
