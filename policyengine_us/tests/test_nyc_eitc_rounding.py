"""Check worksheet rounding over randomized vectors without a simulation.

YAML tests cover household amounts. These tests exercise the rate bounds,
monotonicity, rounding error and decimal ties through the production formula.
"""

import ast
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core import periods
from policyengine_core.parameters import ParameterNode


@pytest.fixture(scope="module")
def nyc_eitc_formula():
    """Load production functions without constructing the package's global model."""
    variables = Path(__file__).resolve().parents[1] / "variables/gov"
    namespace = {"np": np, "max_": np.maximum, "where": np.where}
    for path, class_name, function_name in (
        (
            variables
            / "states/ny/tax/income/adjusted_gross_income/ny_recomputed_federal_agi.py",
            None,
            "get_ny_recomputed_branch",
        ),
        (
            variables / "local/ny/nyc/tax/income/credits/nyc_eitc.py",
            "nyc_eitc",
            "formula",
        ),
    ):
        scope = ast.parse(path.read_text(), filename=str(path))
        if class_name is not None:
            scope = next(
                node
                for node in scope.body
                if isinstance(node, ast.ClassDef) and node.name == class_name
            )
        function = next(
            node
            for node in scope.body
            if isinstance(node, ast.FunctionDef) and node.name == function_name
        )
        module = ast.Module(body=[function], type_ignores=[])
        exec(compile(module, filename=str(path), mode="exec"), namespace)
    return namespace["formula"]


@pytest.fixture(scope="module")
def worksheet_parameters():
    directory = (
        Path(__file__).resolve().parents[1]
        / "parameters/gov/local/ny/nyc/tax/income/credits/eitc"
    )
    eitc = ParameterNode("eitc", directory_path=str(directory))

    def parameters(period):
        node = eitc(period.start)
        for name in reversed(
            ("gov", "local", "ny", "nyc", "tax", "income", "credits", "eitc")
        ):
            node = SimpleNamespace(**{name: node})
        return node

    return parameters


class TaxUnits:
    def __init__(self, incomes, dtype):
        self.incomes = np.asarray(incomes, dtype=dtype)
        self.count = len(incomes)

    def __call__(self, variable, period):
        return {
            "ny_agi": self.incomes,
            "eitc": np.ones(self.count, dtype=self.incomes.dtype),
            "charitable_contributions_ald": np.zeros(
                self.count, dtype=self.incomes.dtype
            ),
        }[variable]


def worksheet_rates(income):
    """Use decimal arithmetic for the worksheet table and line 4."""
    income = Decimal(str(income))
    for lower, upper, rate, subtraction in (
        (0, 5_000, ".30", None),
        (5_000, 7_500, ".30", 4_999),
        (7_500, 15_000, ".25", None),
        (15_000, 17_500, ".25", 14_999),
        (17_500, 20_000, ".20", None),
        (20_000, 22_500, ".20", 19_999),
        (22_500, 40_000, ".15", None),
        (40_000, 42_500, ".15", 39_999),
        (42_500, float("inf"), ".10", None),
    ):
        if lower <= income < upper:
            reduction = (
                Decimal(0)
                if subtraction is None
                else (income - subtraction) * Decimal(".00002")
            )
            rounded = reduction.quantize(Decimal(".0001"), rounding=ROUND_HALF_UP)
            return float(Decimal(rate) - rounded), float(Decimal(rate) - reduction)
    raise AssertionError(f"No worksheet band for {income}")


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@settings(max_examples=100, deadline=None, derandomize=True, database=None)
@given(
    year=st.integers(min_value=2022, max_value=2025),
    incomes=st.lists(
        st.one_of(
            st.integers(min_value=0, max_value=100_000),
            st.integers(min_value=0, max_value=200_000).map(lambda value: value / 2),
        ),
        min_size=1,
        max_size=64,
    ),
)
@example(
    year=2025,
    incomes=[
        5_021.5,
        5_026.5,
        15_021.5,
        15_026.5,
        20_021.5,
        20_026.5,
        40_021.5,
        40_026.5,
    ],
)
@example(
    year=2022,
    incomes=[0, 4_999, 5_000, 7_499, 7_500, 14_999, 15_000, 17_499, 17_500],
)
def test_nyc_eitc_worksheet_rate_invariants(
    nyc_eitc_formula, worksheet_parameters, dtype, year, incomes
):
    incomes = sorted(incomes)
    actual = nyc_eitc_formula(
        TaxUnits(incomes, dtype), periods.period(str(year)), worksheet_parameters
    )
    expected, unrounded = np.asarray([worksheet_rates(income) for income in incomes]).T
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
    assert np.all(actual >= 0.10 - 1e-12)
    assert np.all(actual <= 0.30 + 1e-12)
    assert np.all(np.diff(actual) <= 1e-12)
    assert np.all(np.abs(actual - unrounded) <= 0.00005 + 1e-12)
    np.testing.assert_allclose(
        actual * 10_000, np.rint(actual * 10_000), rtol=0, atol=1e-9
    )


def test_nyc_eitc_rounding_starts_in_2022(nyc_eitc_formula, worksheet_parameters):
    """Keep earlier formula behavior when callers supply the current schedule."""
    schedule = worksheet_parameters(periods.period("2022"))

    def frozen_parameters(period):
        return schedule

    units = TaxUnits([21_000], np.float64)
    before = nyc_eitc_formula(units, periods.period("2021"), frozen_parameters)
    after = nyc_eitc_formula(units, periods.period("2022"), frozen_parameters)
    np.testing.assert_allclose(before, [0.17998], rtol=0, atol=1e-12)
    np.testing.assert_allclose(after, [0.18], rtol=0, atol=1e-12)
