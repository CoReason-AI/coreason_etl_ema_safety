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
from pathlib import Path


def test_logger_initialization_no_dir() -> None:
    """Test logger initialization when logs directory doesn't exist."""
    # To prevent race conditions during parallel tests and PermissionError on Windows,
    # we patch the Path("logs").exists to return False and ensure it creates it.
    from unittest.mock import patch

    import coreason_etl_ema_safety.utils.logger

    with patch.object(Path, "exists", return_value=False), patch.object(Path, "mkdir") as mock_mkdir:
        importlib.reload(coreason_etl_ema_safety.utils.logger)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
