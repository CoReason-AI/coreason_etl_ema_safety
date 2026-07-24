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

from coreason_etl_ema_safety.pipeline import ema_safety_source


@patch("coreason_etl_ema_safety.pipeline.discover_ema_excel_urls")
def test_ema_safety_source_schema(mock_discover_ema_excel_urls: MagicMock) -> None:
    """Test that the DLT source defines the correct schema for the Bronze tables."""
    # Provide a mock URL to generate one resource
    mock_url = "https://www.ema.europa.eu/en/documents/report/medicines-output-periodic_safety_update_report_single_assessments-report_en.xlsx"
    mock_discover_ema_excel_urls.return_value = [mock_url]

    # Initialize the source
    source = ema_safety_source()

    # Get the resource generator
    resources = list(source.resources.values())
    assert len(resources) == 1

    resource = resources[0]
    assert resource.name == "coreason_etl_ema_safety_bronze_periodic_safety_update_report"
    assert resource.write_disposition == "replace"

    # Verify max table nesting is set to 0
    assert source.max_table_nesting == 0

    # Verify column definitions force proper schema
    columns = resource.columns
    assert isinstance(columns, dict), "Columns should be parsed into a dict by dlt"
    assert columns["coreason_id"]["data_type"] == "text"
    assert columns["source_file_url"]["data_type"] == "text"
    assert columns["ingestion_ts"]["data_type"] == "timestamp"
    assert columns["raw_data"]["data_type"] == "json"


@patch("coreason_etl_ema_safety.pipeline.discover_ema_excel_urls")
def test_ema_safety_source_deduplication(mock_discover_ema_excel_urls: MagicMock) -> None:
    """Test that the DLT source deduplicates resources correctly."""
    # Provide multiple URLs that resolve to the same dataset table name
    mock_urls = [
        "https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx",
        "https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_de.xlsx",
    ]
    mock_discover_ema_excel_urls.return_value = mock_urls

    # Initialize the source
    source = ema_safety_source()

    # Despite two URLs, we should only have one resource for this table
    resources = list(source.resources.values())
    assert len(resources) == 1
    assert resources[0].name == "coreason_etl_ema_safety_bronze_medicines"
