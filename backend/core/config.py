import os
import sys
from typing import List, Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:5000"

    # Database (Postgres)
    DATABASE_URL: str = "postgresql://assistiq_user:assistiq_dev_password@localhost:5432/assistiq_db"

    # Security & JWT
    JWT_SECRET_KEY: str = "change-this-to-a-super-secret-high-entropy-key-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Argon2id password hash settings (Local vs Prod per SRS §3.3a)
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 19456  # 19 MiB
    ARGON2_PARALLELISM: int = 1

    # Google OAuth 2.0 / OIDC
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None

    # Google Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Supabase Storage
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_BUCKET_NAME: str = "assistiq-attachments"

    # Email Delivery - Local (Gmail SMTP)
    GMAIL_SMTP_ADDRESS: Optional[str] = None
    GMAIL_SMTP_APP_PASSWORD: Optional[str] = None

    # Email Delivery - Staging / Prod (Brevo HTTP API)
    BREVO_API_KEY: Optional[str] = None
    BREVO_SENDER_EMAIL: str = "support@assistiq.local"
    BREVO_SENDER_NAME: str = "AssistIQ Support"

    # In-Process Scheduler (The Sweep)
    SWEEP_INTERVAL_MINUTES: int = 5

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    def validate_startup_config(self) -> None:
        """
        Validates that required environment variables are present and non-empty.
        Fails fast on boot per SRS §3.3.
        """
        missing_vars: List[str] = []

        # Common mandatory checks
        if not self.DATABASE_URL:
            missing_vars.append("DATABASE_URL")
        if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 16:
            missing_vars.append("JWT_SECRET_KEY (must be at least 16 characters)")

        # In production/staging, enforce critical keys and warn on optional provider keys
        if self.ENVIRONMENT in ["staging", "production"]:
            if not self.GEMINI_API_KEY:
                # If Gemini key is missing, warn or log instead of hard crashing
                print("⚠️ [Config Warning] GEMINI_API_KEY is not set. AI provider will use fallback mode.")

            if not self.GOOGLE_OAUTH_CLIENT_ID or not self.GOOGLE_OAUTH_CLIENT_SECRET:
                print("⚠️ [Config Warning] Google OAuth credentials not configured. Password auth will be active.")

            if not self.BREVO_API_KEY:
                print("⚠️ [Config Warning] Brevo API key not configured. Auto-verified password signup will be active.")

            if not self.SUPABASE_URL or not self.SUPABASE_SERVICE_ROLE_KEY:
                print("⚠️ [Config Warning] Supabase storage keys not configured. Local storage fallback will be active.")

        if missing_vars:
            error_message = (
                "\n" + "=" * 60 + "\n"
                "CRITICAL STARTUP ERROR: Missing required configuration keys:\n"
                + "\n".join(f"  - {var}" for var in missing_vars)
                + f"\nEnvironment: {self.ENVIRONMENT}\n"
                + "=" * 60 + "\n"
            )
            raise RuntimeError(error_message)


settings = Settings()
