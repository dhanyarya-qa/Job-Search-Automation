"""add apply fields

Revision ID: 002
Revises: 001
Create Date: 2026-05-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add apply_link and apply_email columns to jobs table
    op.add_column('jobs', sa.Column('apply_link', sa.String(length=2048), nullable=True))
    op.add_column('jobs', sa.Column('apply_email', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove apply_link and apply_email columns
    op.drop_column('jobs', 'apply_email')
    op.drop_column('jobs', 'apply_link')
