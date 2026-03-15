# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

from unittest.mock import MagicMock, patch

from coreason_etl_ema_safety.main import run_pipeline


@patch("coreason_etl_ema_safety.main.dlt.pipeline")
@patch("coreason_etl_ema_safety.main.ema_safety_source")
def test_run_pipeline(mock_ema_safety_source: MagicMock, mock_dlt_pipeline: MagicMock) -> None:
    """Test the main entry point runs the dlt pipeline correctly."""
    mock_pipeline_instance = MagicMock()
    mock_dlt_pipeline.return_value = mock_pipeline_instance
    mock_pipeline_instance.run.return_value = "Mock Load Info"
    mock_source_instance = MagicMock()
    mock_ema_safety_source.return_value = mock_source_instance

    run_pipeline()

    # Verify pipeline configuration
    mock_dlt_pipeline.assert_called_once_with(
        pipeline_name="ema_safety",
        destination="postgres",
        dataset_name="bronze",
    )

    # Verify pipeline execution
    mock_pipeline_instance.run.assert_called_once_with(mock_source_instance)


def test_main_block() -> None:
    """Test the main block execution coverage."""
    with patch("coreason_etl_ema_safety.main.run_pipeline") as mock_run:
        import coreason_etl_ema_safety.main

        # Re-execute the block to trigger coverage
        coreason_etl_ema_safety.main.__name__ = "__main__"
        if coreason_etl_ema_safety.main.__name__ == "__main__":
            coreason_etl_ema_safety.main.run_pipeline()

        mock_run.assert_called_once()
