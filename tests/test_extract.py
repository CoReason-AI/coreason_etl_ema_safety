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

import polars as pl
import pytest
import requests
import responses

from coreason_etl_ema_safety.extract import discover_ema_excel_urls, process_ema_excel


@responses.activate
def test_process_ema_excel_success() -> None:
    """Test successful downloading, parsing, and serialization of EMA Excel."""
    test_url = "https://www.ema.europa.eu/en/medicines/download/test.xlsx"

    # We mock requests using responses
    responses.add(responses.GET, test_url, body=b"fake_excel_content", status=200)

    # We mock pl.read_excel because fake_excel_content is not a real excel file
    fake_df = pl.DataFrame({"Product number": ["EMEA/1", "EMEA/2"], "Medicine name": ["Med 1", "Med 2"]})

    with patch("coreason_etl_ema_safety.extract.pl.read_excel", return_value=fake_df) as mock_read_excel:
        # consume iterator
        results = list(process_ema_excel(test_url))

        # Check call
        mock_read_excel.assert_called_once()
        args, kwargs = mock_read_excel.call_args
        assert kwargs["engine"] == "calamine"
        assert kwargs.get("read_options", {}).get("skip_rows") == 8
        assert os.path.exists(args[0]) is False  # File should be cleaned up by finally

        # Check results
        assert len(results) == 2

        # Verify schema
        for row in results:
            assert "coreason_id" in row
            assert "source_file_url" in row
            assert "ingestion_ts" in row
            assert "raw_data" in row
            assert row["source_file_url"] == test_url

        assert results[0]["raw_data"]["Product number"] == "EMEA/1"


@responses.activate
def test_process_ema_excel_download_error() -> None:
    """Test behavior on download error (e.g. 404)."""
    test_url = "https://www.ema.europa.eu/en/medicines/download/error.xlsx"
    responses.add(responses.GET, test_url, status=404)

    with pytest.raises(requests.exceptions.HTTPError):
        list(process_ema_excel(test_url))


@responses.activate
def test_discover_ema_excel_urls_success() -> None:
    """Test successful discovery of correct EMA Excel URLs."""
    from coreason_etl_ema_safety.extract import EMA_BASE_URL, EMA_DISCOVERY_URL

    mock_json = [
        {
            "command": "insert",
            "data": """
                <a href="/en/documents/report/medicines-output-medicines-report_en.xlsx">Link</a>
                <a href="/en/documents/report/medicines-output-orphan_designations-report_en.xlsx">Link</a>
            """,
        },
        {
            "command": "insert",
            "data": """
                <a href="/en/documents/report/medicines-output-unrelated-report_en.xlsx">Ignored</a>
                <a href="/en/documents/report/medicines-output-medicines-report_en.xlsx">Duplicate Link</a>
            """,
        },
    ]

    responses.add(responses.GET, EMA_DISCOVERY_URL, json=mock_json, status=200)

    urls = discover_ema_excel_urls()

    assert len(urls) == 2
    assert f"{EMA_BASE_URL}/en/documents/report/medicines-output-medicines-report_en.xlsx" in urls
    assert f"{EMA_BASE_URL}/en/documents/report/medicines-output-orphan_designations-report_en.xlsx" in urls


@responses.activate
def test_discover_ema_excel_urls_error() -> None:
    """Test discover_ema_excel_urls handles HTTP errors."""
    from coreason_etl_ema_safety.extract import EMA_DISCOVERY_URL

    responses.add(responses.GET, EMA_DISCOVERY_URL, status=500)

    with pytest.raises(requests.exceptions.HTTPError):
        discover_ema_excel_urls()
