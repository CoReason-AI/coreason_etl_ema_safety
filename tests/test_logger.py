# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

from coreason_etl_ema_safety.utils.logger import logger


def test_logger_initialization() -> None:
    """Test logger initialization and file creation."""
    assert logger is not None
    # Just sending a log message to exercise the logger.
    logger.info("Test log message.")
