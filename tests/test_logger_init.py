# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

import importlib
import shutil
from pathlib import Path


def test_logger_initialization_no_dir() -> None:
    """Test logger initialization when logs directory doesn't exist."""
    # Remove logs dir if it exists
    log_path = Path("logs")
    if log_path.exists():
        shutil.rmtree(log_path)

    # Re-import logger module to trigger the if not log_path.exists():
    import coreason_etl_ema_safety.utils.logger

    importlib.reload(coreason_etl_ema_safety.utils.logger)

    assert log_path.exists()
