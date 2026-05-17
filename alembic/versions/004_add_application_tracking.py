"""add application tracking

Revision ID: 004
Revises: 003
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create application_tracking table
    op.create_table(
        'application_tracking',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('status_updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_method', sa.String(length=100), nullable=True),
        sa.Column('cover_letter_sent', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('interview_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interview_type', sa.String(length=50), nullable=True),
        sa.Column('interview_notes', sa.Text(), nullable=True),
        sa.Column('offer_received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('offer_amount', sa.String(length=100), nullable=True),
        sa.Column('offer_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_application_tracking_job_id', 'application_tracking', ['job_id'])
    op.create_index('ix_application_tracking_status', 'application_tracking', ['status'])
    op.create_index('ix_application_tracking_updated_at', 'application_tracking', ['updated_at'])


def downgrade() -> None:
    op.drop_index('ix_application_tracking_updated_at', table_name='application_tracking')
    op.drop_index('ix_application_tracking_status', table_name='application_tracking')
    op.drop_index('ix_application_tracking_job_id', table_name='application_tracking')
    op.drop_table('application_tracking')
