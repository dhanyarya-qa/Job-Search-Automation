"""add job tracking fields

Revision ID: 003
Revises: 002
Create Date: 2026-05-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to jobs table
    op.add_column('jobs', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('job_type', sa.String(length=50), nullable=True))
    op.add_column('jobs', sa.Column('experience_level', sa.String(length=50), nullable=True))
    op.add_column('jobs', sa.Column('is_remote', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('jobs', sa.Column('is_priority', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('jobs', sa.Column('sent_to_telegram', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('jobs', sa.Column('telegram_sent_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create indexes for new fields
    op.create_index('ix_jobs_expires_at', 'jobs', ['expires_at'])
    op.create_index('ix_jobs_is_priority', 'jobs', ['is_priority'])
    op.create_index('ix_jobs_sent_to_telegram', 'jobs', ['sent_to_telegram'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_jobs_sent_to_telegram', table_name='jobs')
    op.drop_index('ix_jobs_is_priority', table_name='jobs')
    op.drop_index('ix_jobs_expires_at', table_name='jobs')
    
    # Drop columns
    op.drop_column('jobs', 'telegram_sent_at')
    op.drop_column('jobs', 'sent_to_telegram')
    op.drop_column('jobs', 'is_priority')
    op.drop_column('jobs', 'is_remote')
    op.drop_column('jobs', 'experience_level')
    op.drop_column('jobs', 'job_type')
    op.drop_column('jobs', 'expires_at')
