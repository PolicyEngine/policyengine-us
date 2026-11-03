"""Medicare IRMAA's income lookback fallback and same-year income switch.

The law sets IRMAA on MAGI from two years before the benefit year. When a
simulation holds no input for that year or any earlier one (a single-year
dataset in its data year and the year after, or a household entered for one
year), the MAGI of the earliest year with inputs stands in, deflated to the
lookback year. gov.simulation.medicare_irmaa_uses_current_year_income sets the
charges from the benefit year's own MAGI instead.

Invariants checked here, for every input drawn:
- the Part B IRMAA amount and the Part D surcharge never fall as MAGI rises;
- both are zero below the first IRMAA threshold and positive from it on;
- the fallback is the earliest input year's MAGI times one positive factor,
  the same for every tax unit, so it preserves order and zero;
- provided inputs for the lookback year, or a provided IRMAA MAGI, win;
- the result does not depend on what else was calculated first;
- with the switch on, the charges follow the benefit year's income, so a
  counterfactual earnings change in that year moves them, and with it off a
  known lag income keeps them fixed.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.data.economic_assumptions import DEFAULT_MICRODATA_UPRATING
from policyengine_us.tools.general import earliest_input_year
from policyengine_us.tools.per_capita_uprating import per_capita_path
from policyengine_us.variables.gov.hhs.medicare.eligibility.medicare_irmaa_magi_two_years_prior import (
    LOOKBACK_DEFLATOR,
)
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    user_set_variables,
)

SYSTEM = CountryTaxBenefitSystem()
SWITCH = "gov.simulation.medicare_irmaa_uses_current_year_income"
SAME_YEAR = Reform.from_dict({SWITCH: {"2015-01-01.2100-12-31": True}}, "us")
FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
    "SEPARATE",
]
# Years with brackets of their own; earlier years are backdated from 2024.
BRACKET_YEARS = [2024, 2025, 2026]
DEFLATOR = SYSTEM.parameters.calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita


def deflator(lag_year, source_year):
    return DEFLATOR(f"{lag_year}-01-01") / DEFLATOR(f"{source_year}-01-01")


def senior(person_inputs, tax_unit_inputs=None, reform=None):
    return Simulation(
        situation={
            "people": {"person": {**person_inputs}},
            "tax_units": {
                "tax_unit": {"members": ["person"], **(tax_unit_inputs or {})}
            },
            "households": {"household": {"members": ["person"]}},
        },
        reform=reform,
    )


def part_b_irmaa(sim, year):
    return sim.calculate("gross_medicare_part_b_premium", year) - sim.calculate(
        "base_part_b_premium", year
    )


def part_d_irmaa(sim, year):
    return sim.calculate("income_adjusted_part_d_premium_surcharge", year)


# Fallback


def test_deflator_is_the_dataset_extension_index():
    # Deflating runs the single-year dataset extension backward only while
    # both use the same index.
    assert LOOKBACK_DEFLATOR == per_capita_path(DEFAULT_MICRODATA_UPRATING)


def test_household_with_only_prior_year_inputs_pays_irmaa():
    sim = senior({"age": {2024: 66}, "employment_income": {2024: 200_000}})
    assert earliest_input_year(sim) == 2024
    magi = sim.calculate("medicare_irmaa_magi_two_years_prior", 2025)[0]
    assert magi == pytest.approx(200_000 * deflator(2023, 2024), rel=1e-6)
    assert part_b_irmaa(sim, 2025)[0] > 0
    assert part_d_irmaa(sim, 2025)[0] > 0


def test_multi_year_inputs_use_the_fallback_only_before_the_first_year():
    # As in a dataset extended from 2024: inputs for 2024 and 2025.
    sim = senior(
        {
            "age": {2024: 66, 2025: 67},
            "employment_income": {2024: 200_000, 2025: 250_000},
        }
    )

    def lag(year):
        return sim.calculate("medicare_irmaa_magi_two_years_prior", year)[0]

    def tax_year(year):
        return sim.calculate("medicare_irmaa_tax_year_magi", year)[0]

    assert lag(2025) == pytest.approx(tax_year(2024) * deflator(2023, 2024), rel=1e-6)
    assert lag(2026) == pytest.approx(tax_year(2024))
    assert lag(2027) == pytest.approx(tax_year(2025))
    assert tax_year(2025) == pytest.approx(250_000)


def test_fallback_reads_nothing_before_the_first_input_year():
    sim = senior({"age": {2024: 66}, "employment_income": {2024: 200_000}})
    sim.calculate("gross_medicare_part_b_premium", 2025)
    sim.calculate("income_adjusted_part_d_premium_surcharge", 2025)
    for variable in ["adjusted_gross_income", "medicare_irmaa_tax_year_magi"]:
        years = {period.start.year for period in sim.get_known_periods(variable)}
        assert 2023 not in years, variable


@pytest.mark.parametrize(
    "calculated_first",
    [
        [],
        [("adjusted_gross_income", 2023)],
        [("medicare_irmaa_tax_year_magi", 2023)],
        [("income_tax", 2023), ("income_tax", 2021)],
        [("household_net_income", 2026), ("medicare_irmaa_magi", 2027)],
    ],
)
def test_fallback_does_not_depend_on_calculation_order(calculated_first):
    sim = senior({"age": {2024: 66}, "employment_income": {2024: 200_000}})
    for variable, year in calculated_first:
        sim.calculate(variable, year)
    assert earliest_input_year(sim) == 2024
    assert sim.calculate("medicare_irmaa_magi_two_years_prior", 2025)[
        0
    ] == pytest.approx(200_000 * deflator(2023, 2024), rel=1e-6)


@pytest.mark.parametrize(
    "tax_unit_inputs, expected",
    [
        ({"adjusted_gross_income": {2023: 50_000}}, 50_000),
        ({"medicare_irmaa_tax_year_magi": {2023: 60_000}}, 60_000),
        ({"medicare_irmaa_magi_two_years_prior": {2025: 70_000}}, 70_000),
    ],
)
def test_provided_lookback_income_is_authoritative(tax_unit_inputs, expected):
    sim = senior(
        {"age": {2024: 66}, "employment_income": {2024: 500_000}},
        tax_unit_inputs,
    )
    assert sim.calculate("medicare_irmaa_magi", 2025)[0] == pytest.approx(expected)
    assert part_b_irmaa(sim, 2025)[0] == 0


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(
        st.integers(min_value=-50_000, max_value=2_000_000), min_size=2, max_size=12
    ),
    st.sampled_from([2024, 2025]),
)
def test_fallback_scales_every_tax_unit_by_one_positive_factor(incomes, year):
    # Benefit years 2024 and 2025 look back to 2022 and 2023, before the 2024
    # inputs; every tax unit's lag MAGI is its 2024 MAGI times the same factor.
    people, tax_units, households = {}, {}, {}
    for i, income in enumerate(incomes):
        people[f"p{i}"] = {"age": {2024: 70}, "employment_income": {2024: income}}
        tax_units[f"t{i}"] = {"members": [f"p{i}"]}
        households[f"h{i}"] = {"members": [f"p{i}"]}
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    source = sim.calculate("medicare_irmaa_tax_year_magi", 2024)
    lag = sim.calculate("medicare_irmaa_magi_two_years_prior", year)
    factor = deflator(year - 2, 2024)
    assert factor > 0
    np.testing.assert_allclose(lag, source * factor, rtol=1e-6, atol=0.05)


# Same-year switch


def test_switch_sets_irmaa_from_the_benefit_years_income():
    person = {"age": {2023: 66}, "employment_income": {2023: 50_000, 2025: 300_000}}
    law = senior(person)
    same_year = senior(person, reform=SAME_YEAR)
    assert law.calculate("medicare_irmaa_magi", 2025)[0] == pytest.approx(50_000)
    assert part_b_irmaa(law, 2025)[0] == 0
    assert same_year.calculate("medicare_irmaa_magi", 2025)[0] == pytest.approx(300_000)
    # 2025 single, 200,001 up to 500,000: $406.90 a month.
    assert part_b_irmaa(same_year, 2025)[0] == pytest.approx(12 * 406.9)
    assert part_d_irmaa(same_year, 2025)[0] == pytest.approx(12 * 78.6)


def test_switch_ignores_a_provided_lag_magi():
    sim = senior(
        {"age": {2025: 66}, "employment_income": {2025: 300_000}},
        {"medicare_irmaa_magi_two_years_prior": {2025: 0}},
        reform=SAME_YEAR,
    )
    assert sim.calculate("medicare_irmaa_magi", 2025)[0] == pytest.approx(300_000)


def test_switch_does_not_deflate_benefit_year_income():
    # Inputs only for 2024: the same-year MAGI is 2025 income carried forward
    # from 2024, not the fallback's deflated 2024 income.
    sim = senior(
        {"age": {2024: 66}, "employment_income": {2024: 200_000}}, reform=SAME_YEAR
    )
    assert sim.calculate("medicare_irmaa_magi", 2025)[0] == pytest.approx(
        sim.calculate("medicare_irmaa_tax_year_magi", 2025)[0]
    )


def bump_earnings(sim, year, delta):
    """The earnings change marginal_tax_rate makes, in a branch of ``sim``."""
    branch = sim.get_branch("irmaa_bump")
    inputs = user_set_variables(sim)
    for variable in sim.tax_benefit_system.variables:
        if variable not in inputs or variable == "employment_income":
            branch.delete_arrays(variable)
    branch.set_input(
        "employment_income", year, sim.calculate("employment_income", year) + delta
    )
    return branch


@pytest.mark.parametrize("same_year", [False, True])
def test_counterfactual_earnings_move_irmaa_only_with_the_switch(same_year):
    # The 2023 MAGI is known, so under the law the 2025 charge is fixed; 2025
    # earnings of 199,500 sit just under the 200,001 threshold. The lag MAGI
    # is provided directly: a marginal tax rate branch keeps it, whereas it
    # drops the earnings inputs of years other than the one it changes.
    sim = senior(
        {"age": {2025: 66}, "employment_income": {2025: 199_500}},
        {"medicare_irmaa_magi_two_years_prior": {2025: 150_000}},
        reform=SAME_YEAR if same_year else None,
    )
    before = sim.calculate("gross_medicare_part_b_premium", 2025)[0]
    branch = bump_earnings(sim, 2025, 1_000)
    after = branch.calculate("gross_medicare_part_b_premium", 2025)[0]
    if same_year:
        # 167,001 up to 200,001 is $295.90 a month; above it, $406.90.
        assert after - before == pytest.approx(12 * (406.9 - 295.9))
    else:
        # 133,001 up to 167,001: $185 a month on the $185 standard premium.
        assert before == pytest.approx(12 * (185 + 185))
        assert after == pytest.approx(before)


def test_one_year_household_irmaa_moves_with_that_years_income():
    # Intended: with inputs only for the benefit year, the income two years
    # prior is imputed from that year's income, so a counterfactual earnings
    # change moves the charges even with the switch off. 2026 earnings of
    # 120,500 deflate to 108,653, under the 109,001 threshold; 121,500 deflate
    # to 109,555, over it.
    sim = senior(
        {"age": {2026: 66}, "employment_income": {2026: 120_500}},
    )
    factor = deflator(2024, 2026)
    assert sim.calculate("medicare_irmaa_magi", 2026)[0] == pytest.approx(
        120_500 * factor, rel=1e-6
    )
    before = sim.calculate("gross_medicare_part_b_premium", 2026)[0]
    branch = bump_earnings(sim, 2026, 1_000)
    after = branch.calculate("gross_medicare_part_b_premium", 2026)[0]
    # 2026 single, 109,001 up to 137,001: $81.20 a month.
    assert after - before == pytest.approx(12 * 81.2)


def test_earliest_input_year_skips_variables_the_system_no_longer_has():
    sim = senior(
        {
            "age": {2024: 66},
            "employment_income": {2024: 200_000},
            "tax_exempt_interest_income": {2023: 5},
        }
    )
    assert earliest_input_year(sim) == 2023
    # A reform that removes a variable leaves its recorded input keys behind.
    sim.tax_benefit_system.variables.pop("tax_exempt_interest_income")
    assert earliest_input_year(sim) == 2024


def test_earliest_input_year_skips_neutralized_variables():
    # A neutralized variable reads as its default, so its input is never used:
    # its 2023 input must not turn the 2025 fallback off.
    sim = senior(
        {
            "age": {2024: 66},
            "employment_income": {2024: 200_000},
            "tax_exempt_interest_income": {2023: 5},
        }
    )
    sim.tax_benefit_system.neutralize_variable("tax_exempt_interest_income")
    assert earliest_input_year(sim) == 2024
    assert sim.calculate("medicare_irmaa_magi_two_years_prior", 2025)[
        0
    ] == pytest.approx(200_000 * deflator(2023, 2024), rel=1e-6)


# Bracket properties


def irmaa_by_magi(magis, filing_status, year):
    people, tax_units, households = {}, {}, {}
    for i, magi in enumerate(magis):
        people[f"p{i}"] = {
            "age": {year: 70},
            "is_medicare_eligible": {year: True},
            "medicare_enrolled": {year: True},
        }
        tax_units[f"t{i}"] = {
            "members": [f"p{i}"],
            "filing_status": {year: filing_status},
            "medicare_irmaa_magi": {year: magi},
        }
        households[f"h{i}"] = {"members": [f"p{i}"]}
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    return part_b_irmaa(sim, year), part_d_irmaa(sim, year)


def first_threshold(part, filing_status, year):
    scale = getattr(
        getattr(SYSTEM.parameters(f"{year}-01-01").gov.hhs.medicare, part).irmaa,
        filing_status.lower(),
    )
    return scale.thresholds[1]


@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(
        st.floats(min_value=-1e6, max_value=3e6, width=32),
        min_size=2,
        max_size=15,
    ),
    st.sampled_from(FILING_STATUSES),
    st.sampled_from(BRACKET_YEARS),
)
def test_surcharges_never_fall_as_magi_rises(magis, filing_status, year):
    magis = sorted(magis)
    part_b, part_d = irmaa_by_magi(magis, filing_status, year)
    assert np.all(np.diff(part_b) >= 0)
    assert np.all(np.diff(part_d) >= 0)


@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.data(),
    st.sampled_from(FILING_STATUSES),
    st.sampled_from(BRACKET_YEARS),
)
def test_surcharges_are_zero_below_the_first_threshold(data, filing_status, year):
    # MAGI is stored as float32, so draw values it can hold: 106,000.996 would
    # be stored as the 106,001 threshold itself.
    threshold = first_threshold("part_b", filing_status, year)
    assert threshold == first_threshold("part_d", filing_status, year)
    below = data.draw(
        st.lists(
            st.floats(min_value=-1e6, max_value=threshold, exclude_max=True, width=32),
            min_size=1,
            max_size=10,
        )
    )
    above = data.draw(
        st.lists(
            st.floats(min_value=threshold, max_value=5e6, width=32),
            min_size=1,
            max_size=10,
        )
    )
    part_b, part_d = irmaa_by_magi(below + above, filing_status, year)
    n = len(below)
    assert np.all(part_b[:n] == 0) and np.all(part_d[:n] == 0)
    assert np.all(part_b[n:] > 0) and np.all(part_d[n:] > 0)
