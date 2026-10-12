"""Invariants for the filing requirement of a tax unit nobody can claim.

`tax_unit_is_required_to_file` applies 26 USC 6012(f) for 2018 to 2025 and
6012(a)(1) in other years; the parameter
gov.irs.income.filing_requirement.standard_deduction_rule.applies switches
between them. YAML cases pin the published amounts one case at a time; these
tests check what must hold for every input, which YAML cannot state.

The reference rules below are computed from the published amounts, not from
the model's parameters:

- 6012(a)(1)(A) and (B): a return is required when gross income is at least
  the basic standard deduction plus one additional standard deduction for
  each spouse aged 65 or older. Blindness does not count.
- 6012(f)(1) and (2)(A): a return is required when gross income exceeds the
  standard deduction, which adds the additional standard deduction for age
  and for blindness.
- Under both, a married individual filing separately must file with any
  gross income.

`test_threshold_grid` runs one simulation over every filing status, every
combination of age 65 and blindness for the head and spouse, and gross income
of $0, $1, and a dollar under, at and over each rule's threshold:

1. Differential: the 2026 result equals 6012(a)(1) with the 2026 amounts.
2. Differential: the 2025 result equals 6012(f) with the 2025 amounts.

`test_filing_requirement_properties` draws batches of tax units with
Hypothesis (single, head of household, surviving spouse, separate and joint;
any mix of age, blindness, claimability, wages, interest, dividends, and
self-employment profit or loss; gross income often at a threshold) and runs
each batch, with two variants of every unit, as one simulation. It runs the
batch again under a reform that keeps 6012(f) in force for 2026:

3. Differentials 1 and 2 on every drawn unit nobody can claim.
4. Blindness: for a unit nobody can claim, it never changes the 2026 result.
   For every other unit and year, more blindness never adds a requirement.
5. Age: reaching 65 never adds a requirement, for any unit or year.
6. The switch: with 6012(f) kept for 2026, a unit nobody can claim gets
   6012(f) with the 2026 amounts, and the 2025 result is unchanged.
7. Claimable units are untouched: for a unit whose head or spouse can be
   claimed, the 2026 result is the same with and without the switch. Their
   rule is decision d1395.
8. Inclusion: in 2026, 6012(a)(1) never excuses a unit nobody can claim that
   6012(f) would require to file.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.tests.core.test_filing_requirement_dependent_invariants import (  # noqa: E501
    simulate,
)

YEARS = (2025, 2026)
STATUSES = ["SINGLE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE", "SEPARATE", "JOINT"]

# Basic standard deduction and additional standard deduction by status.
# 2025: Chart A of the 2025 Form 1040 instructions (single $15,750, or
# $17,750 at 65; joint $31,500, $33,100 and $34,700; head of household
# $23,625 and $25,625), https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf
# 2026: Rev. Proc. 2025-32, sec. 4.14,
# https://www.irs.gov/pub/irs-drop/rp-25-32.pdf#page=18
BASIC = {
    2025: {
        "SINGLE": 15_750,
        "HEAD_OF_HOUSEHOLD": 23_625,
        "SURVIVING_SPOUSE": 31_500,
        "SEPARATE": 15_750,
        "JOINT": 31_500,
    },
    2026: {
        "SINGLE": 16_100,
        "HEAD_OF_HOUSEHOLD": 24_150,
        "SURVIVING_SPOUSE": 32_200,
        "SEPARATE": 16_100,
        "JOINT": 32_200,
    },
}
UNMARRIED = ("SINGLE", "HEAD_OF_HOUSEHOLD")
ADDITIONAL = {
    2025: {status: 2_000 if status in UNMARRIED else 1_600 for status in STATUSES},
    2026: {status: 2_050 if status in UNMARRIED else 1_650 for status in STATUSES},
}

GROSS_INCOME_ITEMS = [
    "employment_income",
    "self_employment_income",
    "taxable_interest_income",
    "qualified_dividend_income",
]
VARIANTS = ["base", "blindness_flipped", "aged"]
KEEP_6012_F_IN_2026 = {
    "gov.irs.income.filing_requirement.standard_deduction_rule.applies": {
        "2026-01-01.2100-12-31": True
    }
}


@pytest.fixture(scope="module")
def system_keeping_6012_f():
    """The tax-benefit system with 6012(f) kept for 2026, built once.

    Passing the reform to each Simulation would rebuild the system for every
    Hypothesis example. The simulations only read it, as they read the
    default system, and pytest drops it after this module.
    """
    return CountryTaxBenefitSystem(
        reform=Reform.from_dict(KEEP_6012_F_IN_2026, country_id="us")
    )


def gross_income(unit):
    """Gross income of the head and spouse: no loss reduces it."""
    return sum(
        max(0, adult.get(item, 0))
        for adult in unit["adults"]
        for item in GROSS_INCOME_ITEMS
    )


def threshold(unit, year, rule):
    """The reference threshold, or None for a separate return."""
    status = unit["filing_status"]
    if status == "SEPARATE":
        return None
    aged = sum(adult["age"] >= 65 for adult in unit["adults"])
    blind = sum(adult["is_blind"] for adult in unit["adults"])
    additions = aged if rule == "6012(a)(1)" else aged + blind
    return BASIC[year][status] + additions * ADDITIONAL[year][status]


def reference(unit, year, rule):
    """Whether the reference rule requires a return."""
    income = gross_income(unit)
    limit = threshold(unit, year, rule)
    if limit is None:
        return income > 0
    if rule == "6012(a)(1)":
        return income >= limit
    return income > limit


def rule_in_force(year):
    return "6012(f)" if year <= 2025 else "6012(a)(1)"


def nobody_claimable(unit):
    return not any(
        adult.get("claimed_as_dependent_on_another_return", False)
        for adult in unit["adults"]
    )


def adult(age, blind, claimed=False, **income):
    return {
        "age": age,
        "is_blind": blind,
        "claimed_as_dependent_on_another_return": claimed,
        **income,
    }


def with_gross_income(status, ages, blindness, income):
    """A unit nobody can claim, its gross income split between the adults."""
    adults = [adult(age, blind) for age, blind in zip(ages, blindness)]
    adults[0]["employment_income"] = income // 2
    adults[-1]["taxable_interest_income"] = (
        adults[-1].get("taxable_interest_income", 0) + income - income // 2
    )
    return {"filing_status": status, "adults": adults, "children": []}


def test_threshold_grid():
    units = []
    for status in STATUSES:
        size = 2 if status == "JOINT" else 1
        for ages in np.ndindex(*([2] * size)):
            ages = [65 + 5 * flag if flag else 40 for flag in ages]
            for blindness in np.ndindex(*([2] * size)):
                blindness = [bool(flag) for flag in blindness]
                probe = with_gross_income(status, ages, blindness, 0)
                incomes = {0, 1}
                for year in YEARS:
                    for rule in ("6012(a)(1)", "6012(f)"):
                        limit = threshold(probe, year, rule)
                        if limit is not None:
                            incomes |= {limit - 1, limit, limit + 1}
                units += [
                    with_gross_income(status, ages, blindness, income)
                    for income in sorted(incomes)
                ]
    simulation = simulate(units)
    for year in YEARS:
        required = np.asarray(
            simulation.calculate("tax_unit_is_required_to_file", year)
        )
        expected = np.array(
            [reference(unit, year, rule_in_force(year)) for unit in units]
        )
        mismatched = [
            (unit["filing_status"], gross_income(unit), unit["adults"])
            for unit in np.array(units, dtype=object)[required != expected]
        ]
        assert not mismatched, f"{year}: {mismatched[:3]}"
        # Both answers occur, so the check is not vacuous.
        assert required.any() and not required.all()


# Gross incomes at each reference threshold, a dollar under and over.
BOUNDARIES = sorted(
    {
        BASIC[year][status] + count * ADDITIONAL[year][status] + offset
        for year in YEARS
        for status in STATUSES
        for count in range(5)
        for offset in (-1, 0, 1)
    }
)


@st.composite
def units(draw):
    status = draw(st.sampled_from(STATUSES))
    size = 2 if status == "JOINT" else 1
    claimable = draw(st.booleans())
    adults = [
        adult(
            age=draw(st.sampled_from([19, 40, 64, 65, 66, 80])),
            blind=draw(st.booleans()),
            claimed=claimable and draw(st.booleans()),
        )
        for _ in range(size)
    ]
    # Gross income, often exactly at a threshold, split among the adults'
    # nonnegative items. A self-employment loss does not reduce it.
    total = draw(
        st.one_of(
            st.sampled_from([0, 1] + BOUNDARIES),
            st.integers(0, 45_000),
        )
    )
    slots = [(n, item) for n in range(size) for item in GROSS_INCOME_ITEMS]
    weights = [draw(st.integers(0, 3)) for _ in slots]
    if not any(weights):
        weights[0] = 1
    shares = [total * weight // sum(weights) for weight in weights]
    shares[weights.index(max(weights))] += total - sum(shares)
    for (n, item), share in zip(slots, shares):
        adults[n][item] = share
    loser = draw(st.integers(0, size))
    if loser < size and adults[loser]["self_employment_income"] == 0:
        adults[loser]["self_employment_income"] = -draw(st.integers(1, 20_000))
    return {"filing_status": status, "adults": adults, "children": []}


@st.composite
def unit_variants(draw):
    """A drawn tax unit and its variants, in VARIANTS order."""
    base = draw(units())

    def variant(change):
        copy = {**base, "adults": [dict(adult) for adult in base["adults"]]}
        for person in copy["adults"]:
            change(person)
        return copy

    def flip_blindness(person):
        person["is_blind"] = not person["is_blind"]

    def reach_65(person):
        person["age"] = max(person["age"], 65)

    return [base, variant(flip_blindness), variant(reach_65)]


def blind_count(unit):
    return sum(adult["is_blind"] for adult in unit["adults"])


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(drawn=st.lists(unit_variants(), min_size=8, max_size=24))
def test_filing_requirement_properties(system_keeping_6012_f, drawn):
    flat = [unit for variants in drawn for unit in variants]
    baseline = simulate(flat)
    kept = simulate(flat, tax_benefit_system=system_keeping_6012_f)
    by_variant = {
        name: [variants[n] for variants in drawn] for n, name in enumerate(VARIANTS)
    }
    unclaimable = np.array([nobody_claimable(unit) for unit in by_variant["base"]])
    # Blind adults in the flipped variant less those in the base unit. On a
    # joint return with one blind spouse, flipping swaps who is blind.
    blindness_change = np.array(
        [
            blind_count(flipped) - blind_count(base)
            for base, flipped in zip(
                by_variant["base"], by_variant["blindness_flipped"]
            )
        ]
    )

    def results(simulation, year):
        values = simulation.calculate("tax_unit_is_required_to_file", year)
        columns = np.asarray(values).reshape(-1, len(VARIANTS)).T
        return dict(zip(VARIANTS, columns))

    for year in YEARS:
        required = results(baseline, year)
        required_kept = results(kept, year)
        base = required["base"]
        # Property 3.
        expected = np.array(
            [reference(unit, year, rule_in_force(year)) for unit in by_variant["base"]]
        )
        np.testing.assert_array_equal(
            base[unclaimable],
            expected[unclaimable],
            err_msg=f"{year}: differs from {rule_in_force(year)}",
        )
        # Property 4.
        flipped = required["blindness_flipped"]
        if year >= 2026:
            np.testing.assert_array_equal(
                flipped[unclaimable],
                base[unclaimable],
                err_msg=f"{year}: blindness changed the result",
            )
        checked = ~unclaimable if year >= 2026 else np.ones_like(unclaimable)
        gained = ((blindness_change > 0) & flipped & ~base) | (
            (blindness_change < 0) & base & ~flipped
        )
        assert not (gained & checked).any(), (
            f"{year}: more blindness added a requirement"
        )
        # Property 5.
        assert not (required["aged"] & ~base).any(), (
            f"{year}: reaching 65 added a requirement"
        )
        # Property 6.
        kept_base = required_kept["base"]
        if year >= 2026:
            expected_f = np.array(
                [reference(unit, year, "6012(f)") for unit in by_variant["base"]]
            )
            np.testing.assert_array_equal(
                kept_base[unclaimable],
                expected_f[unclaimable],
                err_msg=f"{year}: the switch did not restore 6012(f)",
            )
            # Property 7.
            np.testing.assert_array_equal(
                kept_base[~unclaimable],
                base[~unclaimable],
                err_msg=f"{year}: the rule changed for a claimable unit",
            )
            # Property 8.
            assert not (kept_base & ~base)[unclaimable].any(), (
                f"{year}: 6012(a)(1) excused a unit 6012(f) requires"
            )
        else:
            np.testing.assert_array_equal(
                kept_base, base, err_msg=f"{year}: the 2026 reform changed {year}"
            )
