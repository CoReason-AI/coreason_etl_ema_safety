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
from typing import Any

import polars as pl
from hypothesis import given
from hypothesis import strategies as st

from coreason_etl_ema_safety.transform import NAMESPACE_EMA_PRODUCT, generate_coreason_ids


def test_generate_coreason_ids_happy_path() -> None:
    """Test generating UUIDs for a standard dataframe with Product number."""
    df = pl.DataFrame(
        {
            "Product number": ["EMEA/H/C/000001", "EMEA/H/C/000002"],
            "Medicine name": ["Medicine A", "Medicine B"],
        }
    )

    result_df = generate_coreason_ids(df)

    assert "coreason_id" in result_df.columns

    expected_id_1 = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, "EMEA/H/C/000001"))
    expected_id_2 = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, "EMEA/H/C/000002"))

    assert result_df["coreason_id"][0] == expected_id_1
    assert result_df["coreason_id"][1] == expected_id_2


def test_generate_coreason_ids_no_product_number() -> None:
    """Test behavior when the dataframe lacks a 'Product number' column."""
    df = pl.DataFrame(
        {
            "Medicine name": ["Medicine A", "Medicine B"],
            "Active substance": ["Substance A", "Substance B"],
        }
    )

    result_df = generate_coreason_ids(df)

    assert "coreason_id" in result_df.columns
    assert result_df["coreason_id"].to_list() == [None, None]


def test_generate_coreason_ids_strip_whitespace() -> None:
    """Test that whitespace is stripped from Product numbers before hashing."""
    df = pl.DataFrame(
        {
            "Product number": ["  EMEA/H/C/000001  ", "\nEMEA/H/C/000002\t"],
        }
    )

    result_df = generate_coreason_ids(df)

    expected_id_1 = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, "EMEA/H/C/000001"))
    expected_id_2 = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, "EMEA/H/C/000002"))

    assert result_df["coreason_id"][0] == expected_id_1
    assert result_df["coreason_id"][1] == expected_id_2


def test_generate_coreason_ids_null_values() -> None:
    """Test behavior with null or missing values in the Product number column."""
    df = pl.DataFrame(
        {
            "Product number": ["EMEA/H/C/000001", None, "EMEA/H/C/000003"],
        }
    )

    result_df = generate_coreason_ids(df)

    expected_id_1 = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, "EMEA/H/C/000001"))
    expected_id_3 = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, "EMEA/H/C/000003"))

    assert result_df["coreason_id"][0] == expected_id_1
    assert result_df["coreason_id"][1] is None
    assert result_df["coreason_id"][2] == expected_id_3


def test_generate_coreason_ids_empty_dataframe() -> None:
    """Test behavior with an empty dataframe."""
    df = pl.DataFrame(schema={"Product number": pl.String, "Medicine name": pl.String})

    result_df = generate_coreason_ids(df)

    assert "coreason_id" in result_df.columns
    assert len(result_df) == 0


@given(st.lists(st.text(), min_size=1, max_size=20))  # type: ignore[misc]
def test_generate_coreason_ids_hypothesis(product_numbers: list[str]) -> Any:
    """Property-based testing for generate_coreason_ids with various string inputs."""
    # We construct a DataFrame from the text elements.
    df = pl.DataFrame({"Product number": product_numbers})
    result_df = generate_coreason_ids(df)

    assert "coreason_id" in result_df.columns
    assert len(result_df) == len(df)

    # Let's perform the exact same stripping polars does.
    # We use a dummy polars operation to see how polars str.strip_chars() handles it.
    expected_df = df.with_columns(pl.col("Product number").cast(pl.String).str.strip_chars().alias("clean"))

    clean_vals = expected_df["clean"].to_list()

    for i, clean_val in enumerate(clean_vals):
        if clean_val:
            expected_id = str(uuid.uuid5(NAMESPACE_EMA_PRODUCT, clean_val))
            assert result_df["coreason_id"][i] == expected_id
        else:
            assert result_df["coreason_id"][i] is None
