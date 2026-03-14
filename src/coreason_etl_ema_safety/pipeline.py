# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

import re
from collections.abc import Iterator

import dlt
from dlt.sources import DltResource

from coreason_etl_ema_safety.extract import discover_ema_excel_urls, process_ema_excel
from coreason_etl_ema_safety.utils.logger import logger


@dlt.source(max_table_nesting=0)  # type: ignore[misc]
def ema_safety_source() -> Iterator[DltResource]:
    """
    AGENT INSTRUCTION: Defines the dlt source for the EMA Safety pipeline.
    Discovers URLs and yields a resource for each dataset with 'replace' write disposition.
    """
    urls = discover_ema_excel_urls()
    logger.info(f"Discovered {len(urls)} EMA excel datasets")

    # Track yielded table names to avoid duplicates
    seen_tables = set()

    for url in urls:
        # Extract dataset name from URL to form the table name
        # e.g. from /medicines-output-medicines-report_en.xlsx -> ema_medicines_report_raw
        match = re.search(r"medicines-output-([a-zA-Z0-9_-]+)-report", url)
        dataset_name = match.group(1).replace("-", "_").replace(" ", "_") if match else "unknown"

        table_name = f"ema_{dataset_name}_raw"

        # Prevent duplicate resource names, which dlt does not allow
        if table_name in seen_tables:
            logger.warning(f"Skipping duplicate resource table name '{table_name}' for url: {url}")
            continue

        seen_tables.add(table_name)
        logger.info(f"Yielding resource for dataset '{dataset_name}' with table name '{table_name}'")

        yield dlt.resource(
            process_ema_excel(url),
            name=table_name,
            table_name=table_name,
            write_disposition="replace",
        )
