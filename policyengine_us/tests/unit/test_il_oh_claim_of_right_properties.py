"""Properties of Illinois's and Ohio's claim of right subtractions.

Illinois (35 ILCS 5/203(a)(2)(P), Schedule M line 15) and Ohio (R.C.
5747.01(A)(12), Schedule of Adjustments line 29) take a repayment of income
held under a claim of right off federal AGI when the federal return claims
section 1341 relief: the credit, or the repayment deduction on a return that
itemizes. The policy cases are in YAML. Which federal method applies, and
whether the return itemizes, come from the federal branch computations, so
these tests check over a grid, with independent simulations:

- each subtraction is the whole repayment exactly when the federal return
  claims relief, and zero otherwise; an eligible return claims relief whenever
  the earlier year's federal tax fell, because a deduction method that wins
  must have lowered tax, which only an itemized deduction does;
- with the credit method fixed, Illinois income tax equals that of a
  simulation with no repayment and the same amount entered through the
  existing Schedule M input, and Ohio taxable income equals that of a
  simulation with no repayment and wages lower by the repayment (where wages
  cover it);
- neither state's income tax ever rises with a repayment, or as the
  repayment grows.
"""

import gc
import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
STATES = ["IL", "OH"]
REPAYMENTS = [0, 2_000, 3_000, 3_001, 10_000, 60_000]
DECREASES = [0, 500, 5_000]
WAGES = [20_000, 80_000, 300_000]
CHARITY = [0, 30_000]
AXES = [STATES, REPAYMENTS, DECREASES, WAGES, CHARITY]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
STATE = np.array([point[0] for point in GRID])
REPAYMENT, DECREASE, WAGE, CHARITABLE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(1, len(AXES))
)
ZEROS = np.zeros_like(REPAYMENT)
IL = STATE == "IL"
OH = STATE == "OH"
THRESHOLD = 3_000
ELIGIBLE_REPAYMENT = np.where(REPAYMENT > THRESHOLD, REPAYMENT, 0)
# Ohio's reference lowers wages by the repayment, so it needs wages at least
# that large.
OH_COMPARABLE = OH & (WAGE >= ELIGIBLE_REPAYMENT)
TOLERANCE = 0.01


def grid_simulation(repayment, method=None, schedule_m=ZEROS, wage_cut=ZEROS):
    """One single-person tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {YEAR: 40},
            "employment_income": {YEAR: WAGE[i] - wage_cut[i]},
            "charitable_cash_donations": {YEAR: CHARITABLE[i]},
            "claim_of_right_repayment": {YEAR: float(repayment[i])},
        }
        tax_unit = {
            "members": [person],
            "claim_of_right_prior_year_tax_decrease": {YEAR: float(DECREASE[i])},
            "il_schedule_m_subtractions": {YEAR: float(schedule_m[i])},
        }
        if method is not None:
            tax_unit["claim_of_right_credit_applies"] = {YEAR: method}
        situation["tax_units"][f"t{i}"] = tax_unit
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {YEAR: STATE[i]},
        }
    return Simulation(situation=situation)


def calculate(simulation, variables):
    return {v: np.asarray(simulation.calculate(v, YEAR)) for v in variables}


@pytest.fixture(scope="module")
def results():
    out = {}
    out["model"] = calculate(
        grid_simulation(REPAYMENT),
        [
            "claim_of_right_section_1341_eligible",
            "claim_of_right_credit_applies",
            "tax_unit_itemizes",
            "claim_of_right_relief_claimed",
            "il_claim_of_right_subtraction",
            "oh_claim_of_right_deduction",
            "state_income_tax",
        ],
    )
    out["none"] = calculate(grid_simulation(ZEROS), ["state_income_tax"])
    out["credit"] = calculate(
        grid_simulation(REPAYMENT, method=True),
        ["il_income_tax", "oh_taxable_income"],
    )
    # Independent references: no repayment, and the same amount entered
    # through paths that existed before these subtractions.
    out["reference"] = calculate(
        grid_simulation(
            ZEROS,
            schedule_m=np.where(IL, ELIGIBLE_REPAYMENT, 0),
            wage_cut=np.where(OH_COMPARABLE, ELIGIBLE_REPAYMENT, 0),
        ),
        ["il_income_tax", "oh_taxable_income"],
    )
    yield out
    gc.collect()


def test_subtraction_is_the_repayment_exactly_when_relief_is_claimed(results):
    r = results["model"]
    eligible = r["claim_of_right_section_1341_eligible"]
    np.testing.assert_array_equal(eligible, REPAYMENT > THRESHOLD)
    claimed = r["claim_of_right_relief_claimed"]
    np.testing.assert_array_equal(
        claimed,
        eligible & (r["claim_of_right_credit_applies"] | r["tax_unit_itemizes"]),
    )
    assert np.all(claimed[eligible & (DECREASE > 0)]), (
        "an eligible return claims relief whenever the earlier tax fell"
    )
    assert (eligible & ~claimed).any(), "the grid should include an unclaimed case"
    expected = np.where(claimed, REPAYMENT, 0)
    np.testing.assert_allclose(
        r["il_claim_of_right_subtraction"], np.where(IL, expected, 0)
    )
    np.testing.assert_allclose(
        r["oh_claim_of_right_deduction"], np.where(OH, expected, 0)
    )


def test_states_match_existing_input_paths(results):
    credit, reference = results["credit"], results["reference"]
    np.testing.assert_allclose(
        credit["il_income_tax"][IL], reference["il_income_tax"][IL], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        credit["oh_taxable_income"][OH_COMPARABLE],
        reference["oh_taxable_income"][OH_COMPARABLE],
        atol=TOLERANCE,
    )


def test_state_tax_never_rises(results):
    with_repayment = results["model"]["state_income_tax"]
    without = results["none"]["state_income_tax"]
    assert np.all(with_repayment <= without + TOLERANCE)
    assert np.any(with_repayment < without - 1), "some repayment should lower tax"
    table = with_repayment.reshape(SHAPE)
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the repayment"
