"""Check daily parameter boundaries that annual household tests cannot reach."""

from datetime import date, timedelta
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.helpers import load_parameter_file


INCOME_LIMIT = load_parameter_file(
    str(
        Path(__file__).resolve().parents[2]
        / "parameters/gov/hhs/medicaid/eligibility/categories/adult/income_limit.yaml"
    ),
    "medicaid_adult_income_limit",
)
STATES = ("VA", "ME", "ID", "UT", "NE")
NO_COVERAGE = float("-inf")


@pytest.mark.parametrize(
    "state, start, before, after",
    [
        ("VA", date(2019, 1, 1), NO_COVERAGE, 1.38),
        ("ME", date(2018, 7, 2), NO_COVERAGE, 1.38),
        ("ID", date(2020, 1, 1), NO_COVERAGE, 1.38),
        ("UT", date(2019, 4, 1), NO_COVERAGE, 1.00),
        ("UT", date(2020, 1, 1), 1.00, 1.38),
        ("NE", date(2020, 10, 1), NO_COVERAGE, 1.38),
    ],
)
def test_adult_income_limit_changes_on_coverage_start(state, start, before, after):
    parameter = INCOME_LIMIT.children[state]
    assert parameter((start - timedelta(days=1)).isoformat()) == before
    assert parameter(start.isoformat()) == after


@settings(max_examples=30, deadline=None, derandomize=True)
@given(
    first=st.dates(min_value=date(2018, 1, 1), max_value=date(2026, 12, 31)),
    second=st.dates(min_value=date(2018, 1, 1), max_value=date(2026, 12, 31)),
)
def test_adult_income_limits_never_fall_during_expansion(first, second):
    earlier, later = sorted((first, second))
    for state in STATES:
        parameter = INCOME_LIMIT.children[state]
        earlier_limit = parameter(earlier.isoformat())
        later_limit = parameter(later.isoformat())
        allowed = {NO_COVERAGE, 1.00, 1.38} if state == "UT" else {NO_COVERAGE, 1.38}
        assert earlier_limit in allowed
        assert later_limit in allowed
        assert earlier_limit <= later_limit


@settings(max_examples=30, deadline=None, derandomize=True)
@given(day=st.dates(min_value=date(2021, 1, 1), max_value=date(2035, 12, 31)))
def test_adult_income_limits_preserve_post_2020_coverage(day):
    for state in STATES:
        assert INCOME_LIMIT.children[state](day.isoformat()) == 1.38
