"""Invariants for the CO, TX and NM SSI supplements over married couples.

Each state pays every SSI recipient on their own (9 CCR 2503-5 3.546-3.548;
HHSC MEPD Handbook H-1500 and H-6000; 8.106.400.10(C) and 8.106.500.10 NMAC),
so a spouse's supplement must not depend on which spouse holds the tax-unit
head role. The grid crosses state, role assignment, the second spouse's
citizenship, the first spouse's resources and an equal pension for both
spouses: 48 married couples (96 people) in one vectorized simulation.

Checked for every person in the grid:

1. Receipt: eligibility holds exactly when the person receives SSI (every
   other program condition is met by construction, and no one reports SSI
   receipt).
2. Role invariance: eligibility and the supplement are identical when the
   head and spouse roles are swapped.
3. Couples: when both spouses are citizens, they have the same eligibility and
   the same supplement.
4. Citizenship: a spouse who fails the SSI citizenship condition is never
   eligible.

YAML covers the source examples and their amounts. Python is needed here to
compare each person across role assignments in one simulation.
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
ANNUAL_PENSION = (0, 3_600)
GRID = tuple(
    product(STATES, ROLE_ORDERS, SECOND_CITIZENSHIP, FIRST_RESOURCES, ANNUAL_PENSION)
)
PROGRAMS = {
    "CO": ("co_state_supplement_eligible", "co_state_supplement"),
    "TX": ("tx_ssi_state_supplement_eligible", "tx_ssi_state_supplement"),
    "NM": ("nm_ssi_state_supplement_eligible", "nm_ssi_state_supplement"),
}
# Each state's program conditions other than SSI receipt.
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
    for index, (state, order, citizenship, resources, pension) in enumerate(GRID):
        conditions = dict(STATE_INPUTS[state])
        ages = conditions.pop("ages")
        members = [f"couple{index}_first", f"couple{index}_second"]
        head = 0 if order == "first_is_head" else 1
        for position, member in enumerate(members):
            person = {
                "age": {YEAR: ages[position]},
                "is_tax_unit_head": {YEAR: position == head},
                "is_tax_unit_spouse": {YEAR: position != head},
                "pension_income": {YEAR: pension},
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
    ssi = simulation.calculate("ssi", PERIOD).reshape(len(GRID), 2)
    eligible = np.zeros_like(ssi, dtype=bool)
    supplement = np.zeros_like(ssi)
    for index, (state, *_rest) in enumerate(GRID):
        eligible_variable, amount_variable = PROGRAMS[state]
        rows = slice(2 * index, 2 * index + 2)
        eligible[index] = simulation.calculate(eligible_variable, PERIOD)[rows]
        supplement[index] = simulation.calculate(amount_variable, PERIOD)[rows]
    return ssi, eligible, supplement


def _case(state, order, citizenship, resources, pension):
    return GRID.index((state, order, citizenship, resources, pension))


def test_eligibility_is_ssi_receipt(results):
    ssi, eligible, _ = results
    np.testing.assert_array_equal(eligible, ssi > 0)


def test_supplement_does_not_depend_on_tax_unit_roles(results):
    _, eligible, supplement = results
    for state, citizenship, resources, pension in product(
        STATES, SECOND_CITIZENSHIP, FIRST_RESOURCES, ANNUAL_PENSION
    ):
        first = _case(state, "first_is_head", citizenship, resources, pension)
        second = _case(state, "second_is_head", citizenship, resources, pension)
        np.testing.assert_array_equal(eligible[first], eligible[second])
        np.testing.assert_allclose(supplement[first], supplement[second])


def test_citizen_spouses_are_treated_alike(results):
    _, eligible, supplement = results
    for index, (_state, _order, citizenship, _resources, _pension) in enumerate(GRID):
        if citizenship == "CITIZEN":
            assert eligible[index, 0] == eligible[index, 1]
            assert supplement[index, 0] == pytest.approx(supplement[index, 1])


def test_spouse_failing_citizenship_condition_is_never_eligible(results):
    _, eligible, supplement = results
    for index, (_state, _order, citizenship, _resources, _pension) in enumerate(GRID):
        if citizenship == "UNDOCUMENTED":
            assert not eligible[index, 1]
            assert supplement[index, 1] == 0


def test_grid_reaches_both_outcomes_for_each_state(results):
    _, eligible, _ = results
    for state in STATES:
        rows = [index for index, case in enumerate(GRID) if case[0] == state]
        assert eligible[rows].any() and not eligible[rows].all()
