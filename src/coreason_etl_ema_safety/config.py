# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

import os


class Settings:
    """
    AGENT INSTRUCTION: Handles application configuration using environment variables.
    Follows 12-Factor App principles.
    """

    def __init__(self) -> None:
        # Core
        self.APP_ENV: str = os.getenv("APP_ENV", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "t", "yes")
        self.SECRET_KEY: str | None = os.getenv("SECRET_KEY")

        # Logging
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        # Postgres Credentials
        self.PGHOST: str = os.getenv("PGHOST", "localhost")
        self.PGPORT: str = os.getenv("PGPORT", "5432")
        self.PGUSER: str = os.getenv("PGUSER", "postgres")
        self.PGPASSWORD: str = os.getenv("PGPASSWORD", "postgres")
        self.PGDATABASE: str = os.getenv("PGDATABASE", "coreason_ema")


settings = Settings()
