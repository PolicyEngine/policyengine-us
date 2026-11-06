"""Properties of the years in which Hawaii's EITC and Act 115 refund apply.

``backdate_parameters`` copies each parameter's first value back to 2015, so
these credits paid in years before they existed until their parameters were
dated. The law:

- Hawaii's earned income tax credit applies to taxable years beginning after
  December 31, 2017 (Act 107, SLH 2017; 2018 Form N-356 instructions, p.2):
  20% of the federal credit, nonrefundable, for 2018-2022, then refundable
  from 2023 (Act 114, SLH 2022), at 40% through 2027 (Act 163, SLH 2023) and
  20% from 2028.
- Act 115 (SLH 2022) refunds went only to filers of a 2021 Form N-11: $300
  per exemption under the federal AGI threshold ($100,000; $200,000 for joint
  filers and surviving spouses) and $100 at or above it (DOTAX Announcement
  2022-03, p.2).

For every grid point, and for Hypothesis-generated batches, in 2015-2026:

- ``hi_act_115_rebate`` is zero before 2021 and equals the announcement's
  table times the number of people on the return in 2021. Its amount
  schedule persists after 2021 for standalone calculations, so later years
  are checked through the refundable credit total instead;
- ``hi_eitc_potential`` is the year's match rate times the federal EITC, so
  it is zero before 2018;
- ``hi_non_refundable_credits`` is zero before 2018 and from 2023, and never
  exceeds the Hawaii EITC or the tax it offsets in 2018-2022;
- refundable credits beyond the food/excise, dependent care and renters'
  credits are the Act 115 refund (2021 only) and the Hawaii EITC (from 2023);
- before 2018, Hawaii income tax is the tax before credits minus the
  refundable credits, since no nonrefundable credit applies.
"""

import itertools

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation

YEARS = list(range(2015, 2027))

# Hawaii EITC match rate by year through 2026 (HRS 235-55.75, Act 107 SLH
# 2017, Act 163 SLH 2023). The 40% rate expires after 2027.
EITC_MATCH = {
    year: 0.0 if year < 2018 else 0.2 if year < 2023 else 0.4 for year in YEARS
}
ACT_115_YEAR = 2021
ACT_115_HIGH, ACT_115_LOW = 300, 100
JOINT_STATUSES = {"JOINT", "SURVIVING_SPOUSE"}
ACT_115_THRESHOLD = {"joint": 200_000, "other": 100_000}

# (adults, children): single, head of household and joint returns.
HOUSEHOLDS = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
WAGES = [0, 4_000, 8_000, 15_000, 40_000, 99_999, 100_000, 150_000, 200_000]
AGES = [30, 70]
GRID = list(itertools.product(HOUSEHOLDS, WAGES, AGES))


def every_year(value):
    return {year: value for year in YEARS}


def hawaii_simulation(points):
    """One Hawaii tax unit per (household, wages, age) point."""
    people, tax_units, households = {}, {}, {}
    for i, ((adults, children), wages, age) in enumerate(points):
        members = []
        for a in range(adults):
            name = f"u{i}_adult{a}"
            people[name] = {
                "age": every_year(age),
                "employment_income": every_year(wages if a == 0 else 0),
            }
            members.append(name)
        for c in range(children):
            name = f"u{i}_child{c}"
            people[name] = {"age": every_year(8 + c)}
            members.append(name)
        tax_units[f"u{i}"] = {"members": members}
        households[f"u{i}"] = {"members": members, "state_code": every_year("HI")}
    return Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )


def act_115_reference(sim, year):
    """DOTAX Announcement 2022-03 table times exemptions, for 2021 only."""
    if year != ACT_115_YEAR:
        return np.zeros(len(sim.calculate("tax_unit_id", year)))
    statuses = sim.calculate("filing_status", year).decode_to_str()
    agi = sim.calculate("adjusted_gross_income", year)
    threshold = np.where(
        np.isin(statuses, list(JOINT_STATUSES)),
        ACT_115_THRESHOLD["joint"],
        ACT_115_THRESHOLD["other"],
    )
    per_exemption = np.where(agi < threshold, ACT_115_HIGH, ACT_115_LOW)
    people = sim.calculate("tax_unit_size", year)
    return per_exemption * people


def check_invariants(sim, year):
    calc = lambda variable: sim.calculate(variable, year)  # noqa: E731

    act_115 = act_115_reference(sim, year)
    if year <= ACT_115_YEAR:
        np.testing.assert_allclose(calc("hi_act_115_rebate"), act_115, atol=0.01)

    eitc_potential = calc("hi_eitc_potential")
    np.testing.assert_allclose(
        eitc_potential, EITC_MATCH[year] * calc("eitc"), atol=0.01
    )

    non_refundable = calc("hi_non_refundable_credits")
    tax_before_credits = calc("hi_income_tax_before_non_refundable_credits")
    if year < 2018 or year >= 2023:
        assert np.all(non_refundable == 0)
    else:
        assert np.all(non_refundable >= 0)
        assert np.all(
            non_refundable <= np.minimum(eitc_potential, tax_before_credits) + 0.01
        )

    base_refundable = (
        calc("hi_food_excise_credit")
        + calc("hi_cdcc")
        + calc("hi_tax_credit_for_low_income_household_renters")
    )
    # act_115 is zero outside 2021, so the refund enters the total only then.
    expected_extra = act_115
    if year >= 2023:
        expected_extra = expected_extra + calc("hi_eitc")
    np.testing.assert_allclose(
        calc("hi_refundable_credits") - base_refundable, expected_extra, atol=0.01
    )

    if year < 2018:
        np.testing.assert_allclose(
            calc("hi_income_tax"),
            tax_before_credits - calc("hi_refundable_credits"),
            atol=0.01,
        )


@pytest.fixture(scope="module")
def grid_sim():
    return hawaii_simulation(GRID)


def test_grid_premises(grid_sim):
    # The grid reaches every filing status the Act 115 table distinguishes
    # here, both sides of each AGI threshold, and a positive federal EITC.
    statuses = set(grid_sim.calculate("filing_status", 2021).decode_to_str())
    assert {"SINGLE", "HEAD_OF_HOUSEHOLD", "JOINT"} <= statuses
    agi = grid_sim.calculate("adjusted_gross_income", 2021)
    assert (agi < 100_000).any() and (agi >= 200_000).any()
    for year in YEARS:
        assert (grid_sim.calculate("eitc", year) > 0).any()


@pytest.mark.parametrize("year", YEARS)
def test_grid_invariants(grid_sim, year):
    check_invariants(grid_sim, year)


def test_act_115_refund_is_paid_only_for_2021(grid_sim):
    # The refund reaches income tax only through the refundable credit total.
    def paid_in(year):
        calc = lambda variable: grid_sim.calculate(variable, year)  # noqa: E731
        extra = calc("hi_refundable_credits") - (
            calc("hi_food_excise_credit")
            + calc("hi_cdcc")
            + calc("hi_tax_credit_for_low_income_household_renters")
        )
        if year >= 2023:
            extra = extra - calc("hi_eitc")
        return extra.sum()

    paid = {year: paid_in(year) for year in YEARS}
    assert paid[ACT_115_YEAR] > 0
    assert all(abs(paid[year]) < 0.01 for year in YEARS if year != ACT_115_YEAR)


def test_hawaii_eitc_starts_in_2018(grid_sim):
    for year in YEARS:
        paid = grid_sim.calculate("hi_eitc_potential", year).sum()
        assert (paid > 0) == (year >= 2018), year


GENERATED_POINTS = st.lists(
    st.tuples(
        st.sampled_from(HOUSEHOLDS),
        st.integers(min_value=0, max_value=300_000),
        st.sampled_from(AGES),
    ),
    min_size=1,
    max_size=8,
)


@settings(max_examples=8, deadline=None)
@given(points=GENERATED_POINTS, year=st.sampled_from(YEARS))
def test_generated_invariants(points, year):
    # Witnesses on each side of the Act 115 thresholds and on the EITC
    # plateau keep every batch from passing vacuously.
    witnesses = [((1, 0), 8_000, 30), ((2, 1), 150_000, 30), ((2, 0), 250_000, 70)]
    check_invariants(hawaii_simulation(points + witnesses), year)
