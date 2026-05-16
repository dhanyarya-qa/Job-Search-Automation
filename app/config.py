"""
Ultimate Job Hunting ATS — Application Settings
Pydantic-based configuration with environment variable support.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────────
    app_name: str = "Ultimate Job Hunting ATS"
    app_env: Literal["development", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = Field(min_length=32)
    debug: bool = False

    # ─── Database ────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://ats_user:ats_password@localhost:5432/job_hunting_ats"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # ─── Redis ───────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_cache_ttl: int = 3600

    # ─── AI Providers ────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_max_tokens: int = 4096

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"

    primary_ai_provider: Literal["openai", "anthropic", "gemini"] = "gemini"

    # ─── Anti-Captcha ────────────────────────────────────────────
    anticaptcha_api_key: str = ""

    # ─── Telegram ────────────────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # ─── JWT Auth ────────────────────────────────────────────────
    jwt_secret_key: str = Field(default="changeme-jwt-secret-32-chars-min!!")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # ─── OTP ─────────────────────────────────────────────────────
    otp_secret_key: str = "changeme-otp-secret"
    otp_expire_minutes: int = 5

    # ─── Email ───────────────────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""

    # ─── Scraper ─────────────────────────────────────────────────
    scraper_headless: bool = True
    scraper_timeout: int = 30000
    scraper_max_retries: int = 3
    scraper_retry_delay: int = 5
    scraper_rate_limit_rpm: int = 30
    proxy_list: str = ""
    use_proxy: bool = False

    # ─── Output ──────────────────────────────────────────────────
    output_dir: str = "./outputs"
    log_level: str = "INFO"
    log_format: str = "json"

    # ─── Dashboard ───────────────────────────────────────────────
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8501
    fastapi_base_url: str = "http://localhost:8000"

    # ─── Candidate Profile ───────────────────────────────────────
    candidate_name: str = "Dhany Arya Pratama"
    candidate_role: str = "QA Engineer | Prompt Engineer | AI Automation"
    candidate_skills: str = "Playwright,Appium,Postman,API Testing,Selenium,Python,JavaScript"

    @property
    def proxy_list_parsed(self) -> list[str]:
        if not self.proxy_list:
            return []
        return [p.strip() for p in self.proxy_list.split(",") if p.strip()]

    @property
    def candidate_skills_list(self) -> list[str]:
        return [s.strip() for s in self.candidate_skills.split(",") if s.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
