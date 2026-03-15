# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

from unittest.mock import patch

from coreason_etl_ema_safety.pipeline import ema_safety_source


def test_ema_safety_source() -> None:
    """Test that the source initializes resources correctly."""
    mock_urls = [
        "https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx",
        "https://www.ema.europa.eu/en/documents/report/medicines-output-referrals-report_en.xlsx",
        "https://www.ema.europa.eu/en/documents/report/medicines-output-paediatric_investigation_plans-report_en.xlsx",
        "https://www.ema.europa.eu/en/documents/report/medicines-output-orphan_designations-report_en.xlsx",
        "https://www.ema.europa.eu/en/documents/report/medicines-output-periodic_safety_update_report_en.xlsx",
        "https://www.ema.europa.eu/en/documents/report/some-other-file_en.xlsx",
    ]

    with patch("coreason_etl_ema_safety.pipeline.discover_ema_excel_urls", return_value=mock_urls):
        source = ema_safety_source()

        # The source acts like a mapping of resources
        # Evaluate how many resources. Since the last two map to 'ema_unknown_raw', one is skipped.
        assert len(source.resources) == 5

        # Check a specific resource's configuration
        medicines_resource = source.resources["ema_medicines_raw"]
        assert medicines_resource.name == "ema_medicines_raw"
        assert medicines_resource.table_name == "ema_medicines_raw"
        assert medicines_resource.write_disposition == "replace"

        # Check unknown dataset
        unknown_resource = source.resources["ema_unknown_raw"]
        assert unknown_resource.name == "ema_unknown_raw"
        assert unknown_resource.table_name == "ema_unknown_raw"
        assert unknown_resource.write_disposition == "replace"

        # Check that max_table_nesting is 0 at the source level
        assert source.max_table_nesting == 0
