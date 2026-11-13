"""California's band and rate divide by one poverty line: the tax family's.

The household is a married couple filing jointly in California, aged 30, where
one spouse can be claimed as a dependent on another return. Its section 36B
tax family has one member (26 CFR 1.36B-1(d)(2); Form 8962 line 1) while the
tax unit has two, so the prior-year guideline for the tax family (aca_fpg) is
the one-person guideline, and the tax unit's two-person guideline is not a
denominator anywhere in the California Premium Subsidy.

The model computes aca_fpg itself here. For drawn whole-dollar incomes:

- ca_premium_subsidy_eligible equals the Program Design (d)(7) band test on
  aca_magi / aca_fpg, with the filing and federal gates held true;
- ca_premium_subsidy_applicable_percentage equals the (d)(4) interpolation at
  the truncated ratio, in the band the exact ratio selects, both ratios over
  aca_fpg.

The guidelines and bands are transcribed, not read from the parameters, and
the reference ratios are exact fractions. Whole-dollar incomes over these
guidelines never fall within float32 rounding of a whole percentage unless
they are exactly on it, so truncation agrees with the model's float32 math.
The examples alternate which spouse is claimable, so both labellings are
exercised.
"""

from fractions import Fraction
from math import floor

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

# Prior-year one-person guideline for the 48 contiguous states and DC: 2025
# for plan year 2026, 2026 for plan year 2027. The two-person guideline,
# $21,150 and $21,640, is the tax unit's and must not be used.
ONE_PERSON_GUIDELINE = {2026: 15_650, 2027: 15_960}
# Program Design (d)(7): household income at or above 100 percent and at or
# below 165 percent (2026 Design) or 200 percent (Final 2027 Design).
BAND = {2026: (Fraction(1), Fraction(165, 100)), 2027: (Fraction(1), Fraction(2))}
# Program Design (d)(4): 0% from 100% up to 150%; above 150% the rate runs
# linearly from the initial to the final percentage at the band's top.
UPPER_BAND = {
    2026: (
        Fraction(15, 10),
        Fraction(165, 100),
        Fraction("0.0319"),
        Fraction("0.0391"),
    ),
    2027: (Fraction(15, 10), Fraction(2), Fraction("0.028"), Fraction("0.0528")),
}
MAX_COUPLES = 64


def reference(year, income):
    guideline = ONE_PERSON_GUIDELINE[year]
    exact = Fraction(max(income, 0), guideline)
    truncated = Fraction(floor(100 * exact), 100)
    floor_, limit = BAND[year]
    eligible = floor_ <= exact <= limit
    start, end, initial, final = UPPER_BAND[year]
    if exact <= start:
        rate = Fraction(0)
    else:
        position = min(max((truncated - start) / (end - start), 0), 1)
        rate = initial + position * (final - initial)
    return eligible, float(rate)


def spouse(claimable, head, year):
    person = {
        "age": {year: 30},
        "is_tax_unit_head": {year: head},
        "is_tax_unit_spouse": {year: not head},
    }
    if claimable:
        person["claimable_as_dependent_on_another_return"] = {year: True}
    return person


def model(year, incomes):
    """One fresh simulation with a couple per income; labels alternate."""
    people, tax_units, households = {}, {}, {}
    for i, income in enumerate(incomes):
        claimable_is_head = i % 2 == 0
        people[f"a{i}"] = spouse(True, claimable_is_head, year)
        people[f"b{i}"] = spouse(False, not claimable_is_head, year)
        tax_units[f"t{i}"] = {
            "members": [f"a{i}", f"b{i}"],
            "filing_status": {year: "JOINT"},
            "aca_magi": {year: float(income)},
        }
        households[f"h{i}"] = {
            "members": [f"a{i}", f"b{i}"],
            "state_code": {year: "CA"},
        }
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    n = len(incomes)
    # Hold the federal and filing gates true, so only the band decides.
    sim.set_input("is_aca_ptc_eligible", year, np.ones(2 * n, dtype=bool))
    sim.set_input("files_return_for_aca_ptc", year, np.ones(n, dtype=bool))
    return (
        sim.calculate("aca_fpg", year),
        sim.calculate("ca_premium_subsidy_eligible", year),
        sim.calculate("ca_premium_subsidy_applicable_percentage", year),
    )


def check(year, incomes):
    fpg, eligible, rate = model(year, incomes)
    assert np.all(fpg == ONE_PERSON_GUIDELINE[year])
    mismatches = []
    for income, e, r in zip(incomes, eligible, rate):
        expected_eligible, expected_rate = reference(year, income)
        if bool(e) != expected_eligible or abs(float(r) - expected_rate) > 1e-6:
            mismatches.append(
                (income, bool(e), float(r), expected_eligible, expected_rate)
            )
    assert not mismatches


@settings(max_examples=25, deadline=None, derandomize=True)
@given(incomes=st.lists(st.integers(-5_000, 60_000), min_size=1, max_size=MAX_COUPLES))
# 100%, 150%, 165% of $15,650 and either side; then the hub's witnesses
# ($20,000, $25,000, $27,000); then 100% and 165% of the two-person $21,150.
@example(
    incomes=[15_649, 15_650, 23_475, 23_476, 25_822, 25_823]
    + [20_000, 25_000, 27_000, 21_150, 34_897, 34_898]
)
def test_2026_band_and_rate_use_the_tax_family_poverty_line(incomes):
    check(2026, incomes)


@settings(max_examples=25, deadline=None, derandomize=True)
@given(incomes=st.lists(st.integers(-5_000, 60_000), min_size=1, max_size=MAX_COUPLES))
# 100%, 150%, 200% of $15,960 and either side; the hub's $35,000 witness;
# 100% and 200% of the two-person $21,640.
@example(
    incomes=[15_959, 15_960, 23_940, 23_941, 31_920, 31_921]
    + [35_000, 21_640, 43_280, 43_281]
)
def test_2027_band_and_rate_use_the_tax_family_poverty_line(incomes):
    check(2027, incomes)


@pytest.mark.parametrize("year", sorted(ONE_PERSON_GUIDELINE))
def test_witnesses_differ_between_the_two_poverty_lines(year):
    """Guards the examples: each witness has a different (in band, above
    150%) outcome over the one-person and two-person guidelines."""
    two_person = {2026: 21_150, 2027: 21_640}[year]
    witnesses = {2026: [20_000, 25_000, 27_000], 2027: [35_000]}[year]
    floor_, limit = BAND[year]
    start = UPPER_BAND[year][0]

    def outcome(ratio):
        return floor_ <= ratio <= limit, ratio > start

    for income in witnesses:
        one = Fraction(income, ONE_PERSON_GUIDELINE[year])
        two = Fraction(income, two_person)
        assert outcome(one) != outcome(two)
