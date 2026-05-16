
---

# `DATABASE_SPEC.md`

```md id="x5cw5x"
# DATABASE_SPEC.md

# DATABASE ENGINE

Use:
- PostgreSQL
- SQLAlchemy Async
- Alembic

---

# REQUIRED TABLES

## jobs
## companies
## ai_analysis
## applications
## followups
## alerts
## otp_sessions
## generated_artifacts
## scraping_logs

---

# REQUIRED FIELDS

## jobs

- id
- job_title
- company_name
- description
- salary
- location
- source_platform
- job_url
- posted_date
- created_at

---

## ai_analysis

- id
- job_id
- match_score
- reasoning
- job_category
- prediction_market
- cover_letter
- interview_questions
- created_at

---

## applications

- id
- job_id
- status
- applied_at
- followup_due
- resume_path
- notes

---

# ORM REQUIREMENTS

Use:
- repository pattern
- async sessions
- migrations
- indexing
- relationships

---

# PERFORMANCE REQUIREMENTS

Add indexes:
- job_title
- company_name
- created_at
- match_score

---

# BACKUP REQUIREMENTS

Implement:
- automatic exports
- CSV snapshots
- JSON backups

---

# TEST REQUIREMENTS

- repository tests
- migration tests
- transaction tests