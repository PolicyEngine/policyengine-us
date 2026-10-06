"""Tests for the 2031 expiry of California's rates above 9.3% and for the
Proposition 3 (2026) contributed reform that would repeal it.

Cal. Const. art. XIII, § 36(f)(2) (single and separate, and through RTC
§ 17045 joint and surviving spouse) and § 36(f)(3) (head of household) apply
the 10.3%, 11.3% and 12.3% rates to taxable years before January 1, 2031.
Proposition 3, SEC. 4, strikes that end date. The YAML cases check dollar
amounts, which depend on CPI projections; these tests check properties that
do not:

- the rate ladder of every filing status in 2030, 2031, 2035 and 2100, under
  the baseline and under the reform;
- for any year and income, the reform changes no threshold and no rate at or
  below 9.3%, adds exactly 1% above each of the three surcharge thresholds
  from 2031 and nothing before, and keeps separate tax equal to single tax and
  joint and surviving spouse tax at twice the single tax on half the income;
- the app path (``Reform.from_dict`` on ``in_effect``) activates the reform
  from a 2031 start and applies it only in the years ``in_effect`` is true;
- the dated windows the reform reads from ``in_effect`` cover exactly the
  instants from 2031 through 2100 at which ``in_effect`` is true; and
- the reform carries each bracket's 2030 rate forward, including a rate the
  user set for 2030.
"""

import functools

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.reforms.states.ca.prop3 import (
    ca_prop3,
    create_ca_prop3_reform,
)
from policyengine_us.reforms.states.ca.prop3.ca_prop3_reform import (
    _active_windows,
)
from policyengine_us.system import system as baseline_system

IN_EFFECT = "gov.contrib.states.ca.prop3.in_effect"
STATUSES = ["single", "separate", "joint", "surviving_spouse", "head_of_household"]
# RTC § 17041(a)(1) and (c)(1) rates, then the § 36(f)(2)-(3) surcharge rates.
BASE_RATES = [0.01, 0.02, 0.04, 0.06, 0.08, 0.093]
PRE_SUNSET_RATES = BASE_RATES + [0.103, 0.113, 0.123]
POST_SUNSET_RATES = BASE_RATES + [0.093, 0.093, 0.093]
SURCHARGE_BRACKETS = [6, 7, 8]
INCOME = 1_000_000


@functools.lru_cache(maxsize=None)
def _bypass_system():
    # The instance YAML `reforms:` tests use; it ignores in_effect.
    return CountryTaxBenefitSystem(reform=ca_prop3)


def _schedule(system, status, year):
    return getattr(
        system.parameters(f"{year}-01-01").gov.states.ca.tax.income.rates, status
    )


def _rates(system, status, year):
    return list(_schedule(system, status, year).rates)


def _tax(system, status, year, income):
    return float(_schedule(system, status, year).calc(np.array([float(income)]))[0])


def _situation(years):
    years = [str(year) for year in years]
    return {
        "people": {"head": {"age": {year: 45 for year in years}}},
        "tax_units": {
            "tax_unit": {
                "members": ["head"],
                "filing_status": {year: "SINGLE" for year in years},
                "ca_taxable_income": {year: INCOME for year in years},
            }
        },
        "households": {
            "household": {
                "members": ["head"],
                "state_code": {year: "CA" for year in years},
            }
        },
    }


def _app_simulation(in_effect_values, years, other_values=None):
    # Mirrors how the app applies the toggle: a dated Reform.from_dict, with the
    # default start_instant.
    reform = Reform.from_dict(
        {IN_EFFECT: in_effect_values, **(other_values or {})},
        country_id="us",
    )
    return Simulation(situation=_situation(years), reform=reform)


def _assert_active_years(simulation, years, active_years):
    for year in years:
        # Before 2031 the baseline already applies the higher rates.
        keeps_higher_rates = year < 2031 or year in active_years
        expected_rates = PRE_SUNSET_RATES if keeps_higher_rates else POST_SUNSET_RATES
        expected_system = _bypass_system() if keeps_higher_rates else baseline_system
        for status in STATUSES:
            assert _rates(simulation.tax_benefit_system, status, year) == (
                pytest.approx(expected_rates)
            ), (status, year)
        tax = simulation.calculate("ca_income_tax_before_credits", year)[0]
        if year >= 2031:
            # The reform raises tax on $1 million in every year from 2031, so
            # the two references differ and the comparison identifies the
            # regime.
            assert _tax(_bypass_system(), "single", year, INCOME) > _tax(
                baseline_system, "single", year, INCOME
            )
        assert tax == pytest.approx(
            _tax(expected_system, "single", year, INCOME), abs=0.01
        ), year


@pytest.mark.parametrize("status", STATUSES)
def test_ca_prop3_rates_all_statuses_and_years(status):
    for year in [2030, 2031, 2035, 2100]:
        expected_baseline = PRE_SUNSET_RATES if year < 2031 else POST_SUNSET_RATES
        assert _rates(baseline_system, status, year) == pytest.approx(
            expected_baseline
        ), year
        # Proposition 3 keeps the 2030 rates in every year through 2100.
        assert _rates(_bypass_system(), status, year) == pytest.approx(
            PRE_SUNSET_RATES
        ), year


@settings(max_examples=300, deadline=None)
@given(
    year=st.integers(min_value=2025, max_value=2040),
    income=st.floats(min_value=0, max_value=50_000_000, allow_nan=False),
)
def test_ca_prop3_preserves_thresholds_lower_rates_and_joint_scaling(year, income):
    reformed_system = _bypass_system()
    for status in STATUSES:
        baseline = _schedule(baseline_system, status, year)
        reformed = _schedule(reformed_system, status, year)
        # Proposition 3 changes no threshold and no rate at or below 9.3%.
        assert list(reformed.thresholds) == list(baseline.thresholds)
        assert list(reformed.rates)[:6] == list(baseline.rates)[:6]
        # From 2031 it adds 1% above each surcharge threshold; before, nothing.
        thresholds = list(baseline.thresholds)
        expected_change = (
            sum(0.01 * max(income - thresholds[i], 0) for i in SURCHARGE_BRACKETS)
            if year >= 2031
            else 0
        )
        change = _tax(reformed_system, status, year, income) - _tax(
            baseline_system, status, year, income
        )
        assert change >= 0
        assert change == pytest.approx(expected_change, rel=1e-9, abs=1e-6)
    for system in [baseline_system, reformed_system]:
        single = _tax(system, "single", year, income)
        # RTC § 17041(a)(1) applies the single schedule to separate returns.
        assert _tax(system, "separate", year, income) == pytest.approx(
            single, rel=1e-9, abs=1e-6
        )
        # RTC § 17045: joint tax is twice the tax on half the income, and a
        # surviving spouse return is treated as a joint return.
        for status in ["joint", "surviving_spouse"]:
            assert _tax(system, status, year, 2 * income) == pytest.approx(
                2 * single, rel=1e-9, abs=1e-6
            )


def test_ca_prop3_app_activation_from_2031():
    years = [2030, 2031, 2035]
    simulation = _app_simulation({"2031-01-01.2100-12-31": True}, years)
    _assert_active_years(simulation, years, active_years={2031, 2035})
    assert simulation.calculate("ca_income_tax_before_credits", 2031)[
        0
    ] == pytest.approx(101_169.10, abs=1)
    # With the toggle off, 2031 tax is the baseline.
    baseline = Simulation(situation=_situation(years))
    assert baseline.calculate("ca_income_tax_before_credits", 2031)[0] == pytest.approx(
        88_942.90, abs=1
    )


@pytest.mark.parametrize(
    "in_effect_values, active_years",
    [
        # True only in 2026, before the sunset: nothing to restore.
        ({"2026-01-01.2026-12-31": True}, set()),
        # A delayed start leaves 2031-2032 at the baseline.
        ({"2033-01-01.2100-12-31": True}, {2033, 2034, 2035}),
        # True, then false in 2033-2034, then true again.
        (
            {"2031-01-01.2032-12-31": True, "2035-01-01.2100-12-31": True},
            {2031, 2032, 2035},
        ),
    ],
)
def test_ca_prop3_respects_delayed_and_bounded_activation(
    in_effect_values, active_years
):
    years = [2030, 2031, 2032, 2033, 2034, 2035]
    simulation = _app_simulation(in_effect_values, years)
    _assert_active_years(simulation, years, active_years)
    reform = create_ca_prop3_reform(
        simulation.tax_benefit_system.parameters, "2024-01-01"
    )
    assert (reform is None) == (not active_years)


def test_ca_prop3_copies_2030_user_rates():
    simulation = _app_simulation(
        {"2031-01-01.2100-12-31": True},
        [2030, 2031, 2035],
        other_values={
            "gov.states.ca.tax.income.rates.single[6].rate": {
                "2030-01-01.2030-12-31": 0.104
            }
        },
    )
    rates = simulation.tax_benefit_system.parameters.gov.states.ca.tax.income.rates
    for year in [2030, 2031, 2035]:
        assert rates.single.brackets[6].rate(f"{year}-01-01") == pytest.approx(0.104)
        # Other schedules keep the statutory 10.3%.
        assert rates.separate.brackets[6].rate(f"{year}-01-01") == pytest.approx(0.103)
    tax_2031 = simulation.calculate("ca_income_tax_before_credits", 2031)[0]
    single_2031 = _schedule(_bypass_system(), "single", 2031)
    bracket_6_income = single_2031.thresholds[7] - single_2031.thresholds[6]
    assert tax_2031 == pytest.approx(
        _tax(_bypass_system(), "single", 2031, INCOME) + 0.001 * bracket_6_income,
        abs=0.01,
    )


# Dated toggle schedules: (start year, start month, end year or None, value).
UPDATES = st.lists(
    st.tuples(
        st.integers(min_value=2020, max_value=2105),
        st.sampled_from([1, 7]),
        st.one_of(st.none(), st.integers(min_value=0, max_value=30)),
        st.booleans(),
    ),
    max_size=5,
)


@settings(max_examples=300, deadline=None)
@given(updates=UPDATES)
def test_ca_prop3_windows_match_dated_in_effect(updates):
    node = ParameterNode("prop3", data={"in_effect": {"values": {"0000-01-01": False}}})
    in_effect = node.in_effect
    for start_year, start_month, length, value in updates:
        start = instant(f"{start_year}-{start_month:02d}-01")
        stop = None if length is None else instant(f"{start_year + length}-12-31")
        in_effect.update(start=start, stop=stop, value=value)
    windows = _active_windows(in_effect)
    # Windows are sorted, disjoint and inside 2031-01-01 through 2100-12-31.
    for (start, stop), (next_start, _) in zip(windows, windows[1:]):
        assert stop < next_start
    for start, stop in windows:
        assert instant("2031-01-01") <= start <= stop <= instant("2100-12-31")
    # They cover exactly the dates from 2031 through 2100 at which the toggle
    # is true, checked on the 1st of January and July of each year.
    for year in range(2025, 2106):
        for month in [1, 7]:
            date = instant(f"{year}-{month:02d}-01")
            covered = any(start <= date <= stop for start, stop in windows)
            expected = 2031 <= year <= 2100 and bool(in_effect(date))
            assert covered == expected, (date, windows)
