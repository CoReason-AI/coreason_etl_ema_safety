# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_ema_safety

import uuid

import polars as pl

NAMESPACE_EMA_PRODUCT = uuid.UUID("e2a4b6c8-1d3f-4e5a-9b7c-8d0f1a2b3c4d")


def generate_coreason_ids(df: pl.DataFrame) -> pl.DataFrame:
    """
    AGENT INSTRUCTION: Compute surrogate keys for the EMA product dataset using UUIDv5.

    This function pre-computes the 'coreason_id' column based on the 'Product number'
    if it exists in the provided DataFrame, deterministically hashing it via UUIDv5.
    If 'Product number' does not exist, 'coreason_id' will be set to None.
    """
    if "Product number" in df.columns:
        df = df.with_columns(pl.col("Product number").cast(pl.String).str.strip_chars().alias("_clean_id"))
        # Empty string should result in None
        df = df.with_columns(
            pl.when(pl.col("_clean_id").is_null() | (pl.col("_clean_id") == ""))
            .then(None)
            .otherwise(pl.col("_clean_id"))
            .alias("_clean_id")
        )
        df = df.with_columns(
            pl.col("_clean_id")
            .map_batches(
                lambda s: pl.Series(
                    [str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, str(x))) if x is not None else None for x in s]
                ),
                return_dtype=pl.String,
            )
            .alias("coreason_id")
        ).drop("_clean_id")
    else:
        # Fallback for tables without Product number
        df = df.with_columns(pl.lit(None).alias("coreason_id"))
    return df
