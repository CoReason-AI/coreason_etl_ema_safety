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
import re
import tempfile
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import polars as pl
import requests

from coreason_etl_ema_safety.transform import generate_coreason_ids

EMA_BASE_URL = "https://www.ema.europa.eu"
EMA_DISCOVERY_URL = f"{EMA_BASE_URL}/en/medicines/download-medicine-data?_wrapper_format=drupal_ajax"

# The TRD requires us to filter for specific target names
TARGET_REPORT_NAMES = {
    "medicines-output-medicines-report",
    "medicines-output-referrals-report",
    "medicines-output-paediatric_investigation_plans-report",
    "medicines-output-orphan_designations-report",
    "medicines-output-periodic_safety_update_report_single_assessments-report",
}


def discover_ema_excel_urls() -> list[str]:
    """
    AGENT INSTRUCTION: Discovers EMA Excel download URLs from the discovery endpoint.
    Filters links to match the exact datasets requested in the FRD.
    """
    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    # EMA requires specific headers to return the drupal_ajax JSON payload
    response = requests.get(EMA_DISCOVERY_URL, headers=headers, timeout=30)
    response.raise_for_status()

    # The JSON response is a list of commands, some containing HTML payloads in 'data'.
    payload = response.json()

    # Extract all HTML strings from the JSON blocks
    html_content = "".join([str(item.get("data", "")) for item in payload if isinstance(item, dict)])

    # Regex to find all matching xlsx documents in the combined HTML payloads
    # Example: /en/documents/report/medicines-output-medicines-report_en.xlsx
    pattern = r"(/en/documents/report/[a-zA-Z0-9_-]+\.xlsx)"

    discovered_urls = []
    seen = set()

    for match in re.finditer(pattern, html_content):
        path = match.group(1)
        url = f"{EMA_BASE_URL}{path}"

        # Filtering logic
        for target in TARGET_REPORT_NAMES:
            if target in path and url not in seen:
                discovered_urls.append(url)
                seen.add(url)
                break

    return discovered_urls


def process_ema_excel(url: str) -> Iterator[dict[str, Any]]:
    """
    AGENT INSTRUCTION: Streams an EMA excel file and serializes rows to raw JSONB payloads safely.

    Adheres strictly to the "Safe Excel Streaming & Serialization Pattern".
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")  # noqa: SIM115
    try:
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
        finally:
            tmp_file.close()  # Release OS lock

        # Read from disk using highly optimized Rust calamine engine (via fastexcel)
        df = pl.read_excel(tmp_file.name, engine="calamine", read_options={"skip_rows": 8})

        # Handle Float NaN vs Null serialization trap
        df = df.fill_nan(None).fill_null(pl.lit(None))

        # Pre-compute UUIDv5
        df = generate_coreason_ids(df)

        ingestion_ts = datetime.now(UTC).isoformat()

        # Prevent dlt Schema Shredding by wrapping in raw_data
        for row in df.to_dicts():
            yield {
                "coreason_id": row.get("coreason_id"),
                "source_file_url": url,
                "ingestion_ts": ingestion_ts,
                "raw_data": row,
            }

    finally:
        os.unlink(tmp_file.name)  # Cross-platform cleanup


# Ensure dlt is imported and available
__all__ = ["discover_ema_excel_urls", "process_ema_excel"]
