"""Virginia filers choose between the credits for low-income taxpayers and the
benefits that bar them.

Va. Code 58.1-339.8(D) allows no low-income credit or Virginia EITC in a year
in which the filers claim the National Guard, military basic pay or federal
and state employee subtraction, an aged or blind exemption, or the age
deduction. A filer entitled to one of those claims whichever gives the greater
benefit, so the model compares Virginia tax in three branches: claiming the
benefits, or forgoing them for the refundable or the nonrefundable credit.

For Virginia households drawn by Hypothesis, with ages, blindness, children
and the listed incomes varied, each test checks a property that holds for
every input:

1. Virginia income tax is the least of the three branches' liabilities, and a
   filer forgoes the benefits only when that strictly lowers tax.
2. Whenever a listed benefit is in the result, so is no credit (the statute's
   bar holds in the outcome, not only in the branches).
3. Becoming entitled to a listed benefit never raises Virginia income tax,
   since the filer can always decline it.
4. The outcome is the same whichever variable a caller calculates first.

YAML cannot state these for all inputs, which is why this file is Python.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    adults,
    dependents,
    money,
)

YEARS = [2022, 2024, 2025, 2026]
TOLERANCE = 0.01
BENEFITS = [
    "va_national_guard_subtraction",
    "va_military_basic_pay_subtraction",
    "va_federal_state_employees_subtraction",
    "va_aged_blind_exemption",
    "va_age_deduction",
]
BRANCHES = [
    "va_income_tax_if_claiming_eitc_disqualifying_benefits",
    "va_income_tax_if_claiming_refundable_eitc",
    "va_income_tax_if_claiming_non_refundable_eitc",
]
REPORTED = [
    "va_income_tax",
    "va_eitc",
    "va_claims_eitc_disqualifying_benefits",
    "va_claims_refundable_eitc",
    *BENEFITS,
]
SETTINGS = settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@st.composite
def filers(draw):
    filer = draw(adults())
    # Low earners reach the EITC and the federal and state employee
    # subtraction; the military incomes reach the other two subtractions.
    filer["employment_income"] = draw(money(25_000))
    filer["state_or_federal_salary"] = draw(money(15_000))
    filer["military_basic_pay"] = draw(money(30_000))
    filer["military_service_income"] = draw(money(6_000))
    return filer


@st.composite
def households(draw):
    return {
        "filers": draw(st.lists(filers(), min_size=1, max_size=2)),
        "dependents": draw(st.lists(dependents(), max_size=3)),
    }


def _situation(units, year, drop=()):
    people, groups = (
        {},
        {
            "tax_units": {},
            "spm_units": {},
            "families": {},
            "marital_units": {},
            "households": {},
        },
    )
    for i, unit in enumerate(units):
        members = []
        for j, amounts in enumerate(unit["filers"]):
            name = f"filer_{i}_{j}"
            people[name] = {
                **{k: v for k, v in amounts.items() if k not in drop},
                "is_tax_unit_head": j == 0,
                "is_tax_unit_spouse": j == 1,
                "is_tax_unit_dependent": False,
            }
            members.append(name)
        groups["marital_units"][f"filers_{i}"] = {"members": list(members)}
        for j, amounts in enumerate(unit["dependents"]):
            name = f"dependent_{i}_{j}"
            people[name] = {
                **amounts,
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
            }
            members.append(name)
            groups["marital_units"][f"dependent_{i}_{j}"] = {"members": [name]}
        for group, prefix in (
            ("tax_units", "tax_unit"),
            ("spm_units", "spm_unit"),
            ("families", "family"),
        ):
            groups[group][f"{prefix}_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "VA"},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _calc(sim, name, year):
    return np.asarray(sim.calculate(name, year), dtype=float)


@SETTINGS
@given(st.sampled_from(YEARS), st.lists(households(), min_size=6, max_size=12))
def test_choice_minimises_tax_and_the_bar_holds(year, units):
    sim = Simulation(situation=_situation(units, year))
    tax = _calc(sim, "va_income_tax", year)
    benefits_tax, refundable_tax, non_refundable_tax = (
        _calc(sim, branch, year) for branch in BRANCHES
    )
    # 1. The result is the best of the three choices.
    best = np.minimum(benefits_tax, np.minimum(refundable_tax, non_refundable_tax))
    np.testing.assert_allclose(tax, best, atol=TOLERANCE)
    claims = _calc(sim, "va_claims_eitc_disqualifying_benefits", year).astype(bool)
    assert (benefits_tax[~claims] > tax[~claims]).all(), (
        "a filer forgoes the benefits without lowering tax"
    )
    # 2. No credit alongside a listed benefit.
    listed = sum(_calc(sim, name, year) for name in BENEFITS)
    for credit in (
        "va_eitc",
        "va_refundable_eitc_if_claimed",
        "va_non_refundable_eitc_if_claimed",
    ):
        amount = _calc(sim, credit, year)
        assert not ((listed > 0) & (amount > 0)).any(), (
            f"{credit} in {year} is paid alongside a listed benefit"
        )
    # Forgone benefits are zero in the result.
    assert not (listed[~claims] > 0).any()


@SETTINGS
@given(st.sampled_from(YEARS), st.lists(households(), min_size=6, max_size=12))
def test_an_entitlement_never_raises_tax(year, units):
    # 3. State or federal salary and military pay reach only the Virginia
    # subtractions, so with them the filer has one more option.
    without = Simulation(
        situation=_situation(
            units,
            year,
            drop=(
                "state_or_federal_salary",
                "military_basic_pay",
                "military_service_income",
            ),
        )
    )
    with_them = Simulation(situation=_situation(units, year))
    before = _calc(without, "va_income_tax", year)
    after = _calc(with_them, "va_income_tax", year)
    rises = after > before + TOLERANCE
    assert not rises.any(), (
        f"Virginia income tax in {year} rises with a subtraction the filer may "
        f"decline: "
        + ", ".join(f"{before[i]:.2f} -> {after[i]:.2f}" for i in np.flatnonzero(rises))
    )


@SETTINGS
@given(st.sampled_from(YEARS), st.lists(households(), min_size=6, max_size=12))
def test_outcome_does_not_depend_on_calculation_order(year, units):
    # 4. Each choice branch fixes both Virginia choices, so a branch never
    # creates its own; the outcome is the same from any entry point.
    reference = Simulation(situation=_situation(units, year))
    reference.calculate("household_net_income", year)
    for first in ("va_eitc", "va_age_deduction", "va_claims_refundable_eitc"):
        sim = Simulation(situation=_situation(units, year))
        sim.calculate(first, year)
        for name in REPORTED:
            np.testing.assert_allclose(
                _calc(sim, name, year),
                _calc(reference, name, year),
                atol=TOLERANCE,
                err_msg=f"{name} changes when {first} is calculated first",
            )
