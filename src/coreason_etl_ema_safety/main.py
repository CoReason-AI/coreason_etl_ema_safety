# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

import dlt

from coreason_etl_ema_safety.pipeline import ema_safety_source
from coreason_etl_ema_safety.utils.logger import logger


def run_pipeline() -> None:
    """
    AGENT INSTRUCTION: Entry point for the EMA safety ETL pipeline.
    Configures and runs the dlt pipeline for the Bronze layer.
    """
    logger.info("Initializing EMA safety dlt pipeline...")

    pipeline = dlt.pipeline(
        pipeline_name="ema_safety",
        destination="postgres",
        dataset_name="bronze",
    )

    load_info = pipeline.run(ema_safety_source())

    logger.info(f"Pipeline executed successfully. Load info: {load_info}")


if __name__ == "__main__":  # pragma: no cover
    run_pipeline()
