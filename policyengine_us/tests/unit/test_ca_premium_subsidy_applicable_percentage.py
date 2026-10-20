"""Properties of the adopted 2026/2027 Design (d)(4) contribution bands.

FTB 3849 Table 1-2 distinguishes exact band eligibility from the truncated
percentage used for the rate lookup. The physical-income properties use
that truncation. Continuity tests supply untruncated lookup fractions to
isolate the interpolation: the actual lookup has whole-percentage steps,
whereas the underlying bands join continuously everywhere except 150%.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period

from policyengine_us.system import system

FPG = 100_000
VARIABLE = "ca_premium_subsidy_applicable_percentage"


def _rates(year, incomes, *, truncate=True):
    """Call the registered formula on vectorized inputs without rebuilding US."""
    calculation_period = period(year)
    incomes = np.asarray(incomes, dtype=float)
    fractions = np.maximum(incomes, 0) / FPG
    if truncate:
        fractions = np.floor(100 * np.maximum(incomes, 0) / FPG) / 100
    inputs = {
        "aca_magi": incomes,
        "aca_magi_fraction": fractions,
        "tax_unit_fpg": np.full(incomes.shape, FPG),
    }

    def tax_unit(name, input_period):
        expected_period = (
            calculation_period.last_year
            if name == "tax_unit_fpg"
            else calculation_period
        )
        assert input_period == expected_period
        return inputs[name]

    formula = system.variables[VARIABLE].get_formula(calculation_period)
    return formula(tax_unit, calculation_period, system.parameters)


@pytest.mark.parametrize("year", [2026, 2027])
@settings(max_examples=100, deadline=None, derandomize=True)
@given(incomes=st.lists(st.integers(-100_000, 600_000), min_size=2, max_size=40))
@example(incomes=[149_999, 150_000, 150_001, 150_999, 151_000])
def test_rate_never_decreases_with_exact_income(year, incomes):
    rates = _rates(year, sorted(incomes))
    assert np.all(np.diff(rates) >= -1e-12)


@pytest.mark.parametrize("year", [2026, 2027])
@settings(max_examples=100, deadline=None, derandomize=True)
@given(income=st.integers(-100_000, 150_000))
@example(income=150_000)
def test_rate_is_zero_at_or_below_exactly_150_percent(year, income):
    assert _rates(year, [income])[0] == 0


@pytest.mark.parametrize("year, starting_rate", [(2026, 0.0319), (2027, 0.0269)])
@settings(max_examples=100, deadline=None, derandomize=True)
@given(income=st.integers(150_001, 150_999))
def test_exact_income_above_150_uses_upper_band_truncated_starting_rate(
    year, starting_rate, income
):
    assert _rates(year, [income])[0] == pytest.approx(starting_rate, rel=0, abs=1e-12)


@pytest.mark.parametrize(
    "year, boundary",
    [(2026, 1), (2026, 1.65), (2027, 1), (2027, 1.65), (2027, 2)],
)
@settings(max_examples=100, deadline=None, derandomize=True)
@given(epsilon=st.floats(min_value=1e-7, max_value=1e-4))
def test_interpolated_bands_are_continuous_except_at_150_percent(
    year, boundary, epsilon
):
    incomes = FPG * np.array([boundary - epsilon, boundary, boundary + epsilon])
    rates = _rates(year, incomes, truncate=False)
    # Each adopted band's slope is below 0.05, so two-sided variation is
    # at most 0.1 * epsilon. An additional band-boundary jump violates this.
    assert np.ptp(rates) <= 0.1 * epsilon + 1e-10
