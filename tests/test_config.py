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
from unittest.mock import patch

from coreason_etl_ema_safety.config import Settings


def test_settings_defaults() -> None:
    """Test the default settings are correctly initialized when no environment variables are present."""
    # Ensure environment variables are clear
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()

        assert settings.APP_ENV == "development"
        assert settings.DEBUG is False
        assert settings.SECRET_KEY is None
        assert settings.LOG_LEVEL == "INFO"
        assert settings.PGHOST == "localhost"
        assert settings.PGPORT == "5432"
        assert settings.PGUSER == "postgres"
        assert settings.PGPASSWORD == "postgres"
        assert settings.PGDATABASE == "coreason_ema"


def test_settings_with_env_vars() -> None:
    """Test settings load values correctly from environment variables."""
    test_env = {
        "APP_ENV": "production",
        "DEBUG": "true",
        "SECRET_KEY": "test-secret",
        "LOG_LEVEL": "DEBUG",
        "PGHOST": "test-db-host",
        "PGPORT": "5433",
        "PGUSER": "testuser",
        "PGPASSWORD": "testpassword",
        "PGDATABASE": "testdb",
    }

    with patch.dict(os.environ, test_env, clear=True):
        settings = Settings()

        assert settings.APP_ENV == "production"
        assert settings.DEBUG is True
        assert settings.SECRET_KEY == "test-secret"  # noqa: S105
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.PGHOST == "test-db-host"
        assert settings.PGPORT == "5433"
        assert settings.PGUSER == "testuser"
        assert settings.PGPASSWORD == "testpassword"
        assert settings.PGDATABASE == "testdb"


def test_settings_debug_variations() -> None:
    """Test different string representations of True for the DEBUG variable."""
    true_values = ["true", "1", "t", "yes", "TRUE", "Yes"]

    for val in true_values:
        with patch.dict(os.environ, {"DEBUG": val}, clear=True):
            settings = Settings()
            assert settings.DEBUG is True

    false_values = ["false", "0", "f", "no", "FALSE", "No"]

    for val in false_values:
        with patch.dict(os.environ, {"DEBUG": val}, clear=True):
            settings = Settings()
            assert settings.DEBUG is False
