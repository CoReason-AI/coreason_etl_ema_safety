# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    AGENT INSTRUCTION: Handles application configuration using environment variables.
    Follows 12-Factor App principles and validates inputs using Pydantic.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    APP_ENV: str = Field(default="development", description="App environment (development, testing, production).")
    DEBUG: bool = Field(default=False, description="Enable debug mode.")
    SECRET_KEY: str | None = Field(default=None, description="Secret key for cryptographic signing.")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Log level for the application.")

    # Postgres Credentials
    PGHOST: str = Field(default="localhost", description="Postgres host address.")
    PGPORT: str = Field(default="5432", description="Postgres port.")
    PGUSER: str = Field(default="postgres", description="Postgres user name.")
    PGPASSWORD: str = Field(default="postgres", description="Postgres password.")
    PGDATABASE: str = Field(default="coreason_ema", description="Postgres database name.")


settings = Settings()
