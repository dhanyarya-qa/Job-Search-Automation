"""Initial schema — All core tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-05-16
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── jobs ─────────────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("salary", sa.String(255)),
        sa.Column("source_platform", sa.String(100), nullable=False),
        sa.Column("job_url", sa.String(2048), nullable=False, unique=True),
        sa.Column("posted_date", sa.DateTime(timezone=True)),
        sa.Column("tags", sa.Text),
        sa.Column("requirements", sa.Text),
        sa.Column("tech_stack", sa.Text),
        sa.Column("job_category_prediction", sa.String(100)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_jobs_job_title", "jobs", ["job_title"])
    op.create_index("ix_jobs_company_name", "jobs", ["company_name"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])

    # ─── companies ────────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("website", sa.String(2048)),
        sa.Column("industry", sa.String(100)),
        sa.Column("size", sa.String(50)),
        sa.Column("location", sa.String(255)),
        sa.Column("tech_stack", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("careers_url", sa.String(2048)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_companies_name", "companies", ["name"])

    # ─── ai_analysis ──────────────────────────────────────────────
    op.create_table(
        "ai_analysis",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("match_score", sa.Float),
        sa.Column("reasoning", sa.Text),
        sa.Column("job_category", sa.String(100)),
        sa.Column("prediction_market", sa.String(255)),
        sa.Column("confidence", sa.Float),
        sa.Column("cover_letter", sa.Text),
        sa.Column("interview_questions", sa.Text),
        sa.Column("portfolio_suggestions", sa.Text),
        sa.Column("ai_provider_used", sa.String(50)),
        sa.Column("tokens_used", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ai_analysis_match_score", "ai_analysis", ["match_score"])
    op.create_index("ix_ai_analysis_created_at", "ai_analysis", ["created_at"])

    # ─── applications ─────────────────────────────────────────────
    op.create_table(
        "applications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("followup_due", sa.DateTime(timezone=True)),
        sa.Column("resume_path", sa.String(512)),
        sa.Column("cover_letter_path", sa.String(512)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ─── followups ────────────────────────────────────────────────
    op.create_table(
        "followups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("follow_up_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("method", sa.String(50), default="email"),
        sa.Column("notes", sa.Text),
        sa.Column("completed", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ─── alerts ───────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("sent_via_telegram", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])

    # ─── otp_sessions ─────────────────────────────────────────────
    op.create_table(
        "otp_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_identifier", sa.String(255), nullable=False),
        sa.Column("otp_hash", sa.String(255), nullable=False),
        sa.Column("purpose", sa.String(50), default="login"),
        sa.Column("is_used", sa.Boolean, default=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_otp_sessions_user_identifier", "otp_sessions", ["user_identifier"])

    # ─── generated_artifacts ──────────────────────────────────────
    op.create_table(
        "generated_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("artifact_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("file_path", sa.String(512)),
        sa.Column("ai_provider", sa.String(50)),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ─── scraping_logs ────────────────────────────────────────────
    op.create_table(
        "scraping_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scraper_type", sa.String(50), nullable=False),
        sa.Column("platform", sa.String(100), nullable=False),
        sa.Column("keyword", sa.String(255)),
        sa.Column("jobs_found", sa.Integer, default=0),
        sa.Column("jobs_saved", sa.Integer, default=0),
        sa.Column("status", sa.String(20), default="running"),
        sa.Column("error_message", sa.Text),
        sa.Column("duration_seconds", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scraping_logs_created_at", "scraping_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("scraping_logs")
    op.drop_table("generated_artifacts")
    op.drop_table("otp_sessions")
    op.drop_table("alerts")
    op.drop_table("followups")
    op.drop_table("applications")
    op.drop_table("ai_analysis")
    op.drop_table("companies")
    op.drop_table("jobs")
