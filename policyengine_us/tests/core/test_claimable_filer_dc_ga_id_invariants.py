"""District of Columbia, Georgia and Idaho rules for a filer who can be claimed
as a dependent.

A return on which the filer, or on a joint return either spouse, can be claimed
as a dependent outside the filing exception has no dependents (IRC 152(b)(1)).
DC's property tax credit needs a claimant who was not a dependent or is 65 or
older; Georgia's low income credit and 2023 surplus refund need one filer who
qualifies; Idaho's food tax credit leaves out each filer who can be claimed.

For couples drawn by Hypothesis and a seeded population in these states,
claimability, actual claims and the filing exception vary independently,
subject to an actual claim requiring claimability and excluding the exception:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed, with fallback claimability
   and no filing exception, never raises the outputs in MONOTONE (amounts not
   capped by a tax liability that the claim can raise).
3. Identities: a return with a claimable filer outside the filing exception has
   no DC keep child care affordable credit or child tax credit and its Idaho
   food tax credit is at most one filer's amount; a return on which every
   filer can be claimed has no Georgia low income credit.

Hypothesis batches check 1 and 3; the seeded population checks 1, 2 and 3.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us.tests.core.test_claimable_filer_federal_invariants import (
    check_monotone,
    check_swap,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
    _calc,
    _crafted_cases,
    _seeded_couples,
    adults,
    dependents,
)

STATES = ["DC", "GA", "ID"]
YEARS = [2021, 2023, 2025, 2026]
MONOTONE = [
    "dc_ptc",
    "dc_eitc",
    "dc_kccatc",
    "dc_ctc",
    "ga_exemptions",
    "ga_low_income_credit_potential",
    "ga_ctc_potential",
    "id_grocery_credit",
    "id_household_and_dependent_care_expense_deduction",
]
OUTPUTS = MONOTONE + ["ga_surplus_tax_rebate", "id_2022_rebate"]


@st.composite
def couples(draw):
    claimable = draw(st.sampled_from(CLAIM_PATTERNS))
    claimed = tuple(can_claim and draw(st.booleans()) for can_claim in claimable)
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": claimed,
        "claimable": claimable,
        "exception": tuple(
            not is_claimed and draw(st.booleans()) for is_claimed in claimed
        ),
    }


def _identities(sim, year):
    blocked_filer = (
        _calc(
            sim, "head_or_spouse_is_dependent_elsewhere_without_filing_exception", year
        )
        > 0
    )
    for name in ("dc_kccatc", "dc_ctc"):
        assert not _calc(sim, name, year)[blocked_filer].any(), (
            f"{name} in {year} is positive on a return with a claimable filer "
            "outside the filing exception"
        )
    # Georgia's low income credit needs one filer who cannot be claimed.
    every_filer = _calc(sim, "every_filer_is_dependent_elsewhere", year) > 0
    assert not _calc(sim, "ga_low_income_credit_potential", year)[every_filer].any()
    # Outside the filing exception, at most the independent filer keeps a
    # food tax credit; no dependent child qualifies.
    one_filer = _one_filer_food_amount(sim, year)
    grocery = _calc(sim, "id_grocery_credit", year)
    assert (grocery[blocked_filer] <= one_filer + 0.01).all()


def _one_filer_food_amount(sim, year):
    p = sim.tax_benefit_system.parameters(f"{year}-01-01").gov.states.id.tax.income
    amount = p.credits.grocery.base.amount
    if p.credits.grocery.aged.in_effect:
        amount += p.credits.grocery.aged.amount
    return amount


def _with_independent_claim_inputs(units):
    rng = np.random.default_rng(20261018)
    result = []
    for unit in units:
        claimable = CLAIM_PATTERNS[int(rng.integers(len(CLAIM_PATTERNS)))]
        claimed = tuple(can_claim and bool(rng.integers(2)) for can_claim in claimable)
        exception = tuple(
            not is_claimed and bool(rng.integers(2)) for is_claimed in claimed
        )
        result.append(
            {
                **unit,
                "claimable": claimable,
                "claimed": claimed,
                "exception": exception,
            }
        )
    return result


@pytest.mark.parametrize(
    "year,state,expected",
    [
        (2025, "ID", {"id_grocery_credit": 310}),
        (2026, "DC", {"dc_kccatc": 1_000, "dc_ctc": 1_000}),
    ],
)
def test_dc_id_filing_exception_restores_children_under_both_labels(
    year, state, expected
):
    # The claimable adult keeps the exception and the independent spouse and
    # child keep their credits when either adult is labelled head. Idaho still
    # excludes the claimable adult's own $155 food tax credit.
    units = [
        {
            "state": state,
            "adults": [{"age": 26, "employment_income": 2_000}, {"age": 30}],
            "dependents": [{"age": 2, "pre_subsidy_childcare_expenses": 1_000}],
            "claimed": (False, False),
            "claimable": (True, False),
            "exception": (True, False),
        }
    ]
    if state == "ID":
        # Isolate the dependency rule from SNAP and other month exclusions.
        for person in units[0]["adults"] + units[0]["dependents"]:
            person["id_grocery_credit_qualified_months"] = 12

    def exception_identities(sim, year):
        for name, amount in expected.items():
            np.testing.assert_allclose(_calc(sim, name, year), [amount, amount])
        _identities(sim, year)

    check_swap(units, year, OUTPUTS, exception_identities)


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_dc_ga_id_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities)


@pytest.mark.parametrize("year", YEARS)
def test_dc_ga_id_claimable_filer_rules_seeded_population(year):
    seeded = _seeded_couples(STATES, per_state=3)
    crafted = _crafted_cases(STATES)
    # Core fills omitted people with input defaults once any person supplies
    # claimability, so express the crafted cases' legacy values explicitly in
    # the swap simulation. The monotonicity simulation retains their fallback.
    explicit_crafted = [
        {**unit, "claimable": unit["claimed"], "exception": (False, False)}
        for unit in crafted
    ]
    check_swap(
        _with_independent_claim_inputs(seeded) + explicit_crafted,
        year,
        OUTPUTS,
        _identities,
    )
    # The shared monotonicity helper toggles actual claims while keeping any
    # explicit claimability and exception inputs fixed. Retain the legacy
    # population here so every variant is valid and claimability changes with
    # the actual claim; the swap population independently exercises all inputs.
    check_monotone(seeded + crafted, year, MONOTONE, _identities)
