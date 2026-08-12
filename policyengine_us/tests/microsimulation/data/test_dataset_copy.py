"""
Tests for USSingleYearDataset.copy / USMultiYearDataset.copy deep/shallow
semantics.

With pandas copy-on-write, ``copy(deep=False)`` shares column buffers
until a column is reassigned while keeping the original isolated.
"""

import numpy as np
import pandas as pd

from policyengine_us.data.dataset_schema import (
    USMultiYearDataset,
    USSingleYearDataset,
)
from policyengine_us.tests.microsimulation.data.fixtures.test_extend_single_year_dataset import (  # noqa: E501
    BASE_YEAR,
    EMPLOYMENT_INCOME_BASE,
    build_single_year_dataset,
)


def test_deep_copy_does_not_share_memory():
    base = build_single_year_dataset()
    copied = base.copy()
    for name, base_df, copied_df in zip(base.table_names, base.tables, copied.tables):
        for col in base_df.columns:
            assert not np.shares_memory(base_df[col].values, copied_df[col].values), (
                f"deep copy shares memory for {name}.{col}"
            )


def test_shallow_copy_shares_memory():
    base = build_single_year_dataset()
    copied = base.copy(deep=False)
    for name, base_df, copied_df in zip(base.table_names, base.tables, copied.tables):
        for col in base_df.columns:
            assert np.shares_memory(base_df[col].values, copied_df[col].values), (
                f"shallow copy does not share memory for {name}.{col}"
            )


def test_copy_preserves_time_period_and_values():
    base = build_single_year_dataset()
    for deep in (True, False):
        copied = base.copy(deep=deep)
        assert copied.time_period == base.time_period
        for base_df, copied_df in zip(base.tables, copied.tables):
            pd.testing.assert_frame_equal(base_df, copied_df)


def test_shallow_copy_column_assignment_isolates():
    base = build_single_year_dataset()
    copied = base.copy(deep=False)
    copied.person["employment_income"] = copied.person["employment_income"] * 1.10
    # The original is untouched...
    assert (base.person["employment_income"] == EMPLOYMENT_INCOME_BASE).all()
    # ...and unassigned columns still share memory.
    assert np.shares_memory(base.person["age"].values, copied.person["age"].values)


def test_multi_year_deep_copy_does_not_share_memory():
    base = build_single_year_dataset()
    next_year = base.copy()
    next_year.time_period = str(BASE_YEAR + 1)
    multi = USMultiYearDataset(datasets=[base, next_year])

    deep = multi.copy()
    assert deep.years == multi.years
    assert not np.shares_memory(
        deep[BASE_YEAR].person["age"].values,
        multi[BASE_YEAR].person["age"].values,
    )


def test_multi_year_shallow_copy_shares_memory():
    base = build_single_year_dataset()
    next_year = base.copy()
    next_year.time_period = str(BASE_YEAR + 1)
    multi = USMultiYearDataset(datasets=[base, next_year])

    shallow = multi.copy(deep=False)
    assert shallow.years == multi.years
    assert np.shares_memory(
        shallow[BASE_YEAR].person["age"].values,
        multi[BASE_YEAR].person["age"].values,
    )
