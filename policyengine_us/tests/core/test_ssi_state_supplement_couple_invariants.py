"""Invariants for the CO, TX and NM SSI supplements over married couples.

Each state pays every SSI recipient on their own (9 CCR 2503-5 3.546-3.549;
HHSC MEPD Handbook H-1500 and H-6000; 8.106.400.10(C) and 8.106.500.10 NMAC),
so a spouse's supplement must not depend on which spouse holds the tax-unit
head role. The grid crosses state, role assignment, the second spouse's
citizenship, the first spouse's resources and the two spouses' monthly
pensions (none, $300 each, or $400 and $200): 72 married couples (144 people)
in one vectorized simulation.

Checked for every person in the grid:

1. Receipt: anyone paid SSI is eligible, and no one is eligible without being
   eligible for SSI with countable income not over the payment standard (no
   one in the grid reports SSI receipt, and every other program condition is
   met by construction). In Colorado and New Mexico eligibility is exactly a
   positive SSI payment.
2. Role invariance: eligibility and the supplement are identical when the
   head and spouse roles are swapped.
3. Couples: two citizen spouses with the same income have the same
   eligibility and the same supplement.
4. Citizenship: a spouse who fails the SSI citizenship condition is never
   eligible.
5. Colorado couple total: when both spouses of a joint SSI claim receive
   AND-CS and have only unearned income, the two grants sum to twice the
   grant standard less the couple's federal SSI and pooled countable income,
   as in SSA's Colorado couple payment level (1,398 = 2 x 699 in January
   2011), however 3.549(A) divides their own income between them. (Earnings
   break the identity: 3.549(A)(1) deducts $65 for each client, where SSI
   deducts $65 once for the couple.)

YAML covers the source examples and their amounts. Python is needed here to
compare each person across role assignments and spouses in one simulation.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation


YEAR = 2026
PERIOD = "2026-01"
STATES = ("CO", "TX", "NM")
ROLE_ORDERS = ("first_is_head", "second_is_head")
SECOND_CITIZENSHIP = ("CITIZEN", "UNDOCUMENTED")
FIRST_RESOURCES = (0, 4_000)
# Monthly pensions of the first and second spouse.
PENSIONS = ((0, 0), (300, 300), (400, 200))
GRID = tuple(
    product(STATES, ROLE_ORDERS, SECOND_CITIZENSHIP, FIRST_RESOURCES, PENSIONS)
)
PROGRAMS = {
    "CO": ("co_state_supplement_eligible", "co_state_supplement"),
    "TX": ("tx_ssi_state_supplement_eligible", "tx_ssi_state_supplement"),
    "NM": ("nm_ssi_state_supplement_eligible", "nm_ssi_state_supplement"),
}
# Each state's program conditions other than SSI.
STATE_INPUTS = {
    # AND-CS: blind or disabled, ages 0-59.
    "CO": dict(
        ages=(50, 52),
        is_disabled=True,
        meets_ssi_disability_criteria=True,
    ),
    # SSI recipient in a Medicaid facility on the $30 reduced benefit.
    "TX": dict(
        ages=(72, 70),
        is_in_medicaid_facility=True,
        ssi_lives_in_medical_treatment_facility=True,
        ssi_medicaid_pays_majority_of_care=True,
    ),
    # SSI recipient aged 18 or over in a licensed ARSCH home.
    "NM": dict(ages=(68, 66), is_in_adult_residential_care=True),
}


def _situation():
    groups = ("tax_units", "marital_units", "spm_units", "families", "households")
    situation = {"people": {}, **{group: {} for group in groups}}
    for index, (state, order, citizenship, resources, pensions) in enumerate(GRID):
        conditions = dict(STATE_INPUTS[state])
        ages = conditions.pop("ages")
        members = [f"couple{index}_first", f"couple{index}_second"]
        head = 0 if order == "first_is_head" else 1
        for position, member in enumerate(members):
            person = {
                "age": {YEAR: ages[position]},
                "is_tax_unit_head": {YEAR: position == head},
                "is_tax_unit_spouse": {YEAR: position != head},
                "pension_income": {YEAR: 12 * pensions[position]},
                "ssi_countable_resources": {YEAR: resources if position == 0 else 0},
                "immigration_status_str": {
                    YEAR: citizenship if position == 1 else "CITIZEN"
                },
            }
            person.update({name: {YEAR: value} for name, value in conditions.items()})
            situation["people"][member] = person
        for group in groups:
            situation[group][f"{group}_{index}"] = {"members": members}
        situation["households"][f"households_{index}"]["state_code"] = {YEAR: state}
    return situation


@pytest.fixture(scope="module")
def results():
    simulation = Simulation(situation=_situation())

    def couples(variable, period=PERIOD):
        return simulation.calculate(variable, period).reshape(len(GRID), 2)

    eligible = np.zeros((len(GRID), 2), dtype=bool)
    supplement = np.zeros((len(GRID), 2))
    for state, (eligible_variable, amount_variable) in PROGRAMS.items():
        rows = [index for index, case in enumerate(GRID) if case[0] == state]
        eligible[rows] = couples(eligible_variable)[rows]
        supplement[rows] = couples(amount_variable)[rows]
    parameters = simulation.tax_benefit_system.parameters(PERIOD)
    return dict(
        grant_standard=parameters.gov.states.co.ssa.state_supplement.grant_standard,
        ssi=couples("ssi"),
        ssi_eligible=couples("is_ssi_eligible"),
        uncapped_ssi=couples("uncapped_ssi"),
        joint=couples("ssi_claim_is_joint", YEAR),
        federal_countable=couples("ssi_countable_income", YEAR) / 12,
        eligible=eligible,
        supplement=supplement,
    )


def _rows(**fixed):
    names = ("state", "order", "citizenship", "resources", "pensions")
    return [
        index
        for index, case in enumerate(GRID)
        if all(case[names.index(name)] == value for name, value in fixed.items())
    ]


def test_eligibility_follows_ssi_eligibility(results):
    paid = results["ssi"] > 0
    within_limit = results["ssi_eligible"] & (results["uncapped_ssi"] >= 0)
    eligible = results["eligible"]
    assert not (paid & ~eligible).any()
    assert not (eligible & ~within_limit).any()
    for state in ("CO", "NM"):
        rows = _rows(state=state)
        np.testing.assert_array_equal(eligible[rows], paid[rows])


def test_supplement_does_not_depend_on_tax_unit_roles(results):
    for state, citizenship, resources, pensions in product(
        STATES, SECOND_CITIZENSHIP, FIRST_RESOURCES, PENSIONS
    ):
        first, second = (
            GRID.index((state, order, citizenship, resources, pensions))
            for order in ROLE_ORDERS
        )
        for name in ("eligible", "supplement"):
            np.testing.assert_allclose(results[name][first], results[name][second])


def test_citizen_spouses_with_equal_income_are_treated_alike(results):
    for index, (_, _, citizenship, _, pensions) in enumerate(GRID):
        if citizenship == "CITIZEN" and pensions[0] == pensions[1]:
            for name in ("eligible", "supplement"):
                assert results[name][index, 0] == pytest.approx(results[name][index, 1])


def test_spouse_failing_citizenship_condition_is_never_eligible(results):
    rows = _rows(citizenship="UNDOCUMENTED")
    assert not results["eligible"][rows, 1].any()
    assert not results["supplement"][rows, 1].any()


def test_colorado_couple_total_matches_pooled_computation(results):
    rows = [
        index
        for index in _rows(state="CO")
        if results["joint"][index].all() and results["eligible"][index].all()
    ]
    assert rows
    pooled = (
        2 * results["grant_standard"]
        - results["ssi"][rows].sum(axis=1)
        - results["federal_countable"][rows].sum(axis=1)
    )
    np.testing.assert_allclose(results["supplement"][rows].sum(axis=1), pooled)


def test_grid_reaches_both_outcomes_for_each_state(results):
    for state in STATES:
        rows = _rows(state=state)
        assert results["eligible"][rows].any()
        assert not results["eligible"][rows].all()
