"""Properties of Illinois's and Ohio's claim of right subtractions.

Illinois (35 ILCS 5/203(a)(2)(P), Schedule M line 15) and Ohio (R.C.
5747.01(A)(12), Schedule of Adjustments line 29) take a repayment of income
held under a claim of right off federal AGI when the federal return claims
section 1341 relief: the credit, or the repayment deduction on a return that
itemizes. The policy cases are in YAML. Which federal method applies, and
whether the return itemizes, come from the federal branch computations, so
these tests compare simulations over a grid of repayments, earlier-year
decreases, wages and charity, each against a reference that does not use the
new variables:

- with the federal credit method fixed, or the deduction method fixed on a
  return that itemizes, Illinois income tax equals that of a simulation with
  no repayment and the same amount entered through the existing Schedule M
  input, and Ohio taxable income equals that of a simulation with no
  repayment and wages lower by the repayment (where wages cover it); with the
  deduction method fixed on a return taking the standard deduction, both equal
  a simulation with no repayment;
- with the method chosen by the model, an eligible return gets that relief
  whenever the earlier year's federal tax fell, because a winning deduction
  must have lowered tax, which only an itemized deduction does;
- for these single filers, neither state's income tax ever rises with a
  repayment, or as it grows (on a joint Ohio return the deduction can cost the
  joint filing credit; see the YAML).
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


def grid_simulation(repayment, tax_unit_inputs=None, schedule_m=ZEROS, wage_cut=ZEROS):
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
        for name, value in (tax_unit_inputs or {}).items():
            tax_unit[name] = {YEAR: value}
        situation["tax_units"][f"t{i}"] = tax_unit
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {YEAR: STATE[i]},
        }
    return Simulation(situation=situation)


def calculate(simulation, variables):
    return {v: np.asarray(simulation.calculate(v, YEAR)) for v in variables}


METHODS = {
    "credit": {"claim_of_right_credit_applies": True},
    "deduction_itemizing": {
        "claim_of_right_credit_applies": False,
        "tax_unit_itemizes": True,
    },
    "deduction_standard": {
        "claim_of_right_credit_applies": False,
        "tax_unit_itemizes": False,
    },
}
OUTPUTS = ["il_income_tax", "oh_taxable_income", "state_income_tax"]


@pytest.fixture(scope="module")
def results():
    out = {"model": calculate(grid_simulation(REPAYMENT), OUTPUTS)}
    for name, inputs in METHODS.items():
        out[name] = calculate(
            grid_simulation(REPAYMENT, tax_unit_inputs=inputs), OUTPUTS
        )
    out["none"] = calculate(grid_simulation(ZEROS), OUTPUTS)
    # Independent reference: no repayment, and the same amount entered through
    # paths that existed before these subtractions.
    out["reference"] = calculate(
        grid_simulation(
            ZEROS,
            schedule_m=np.where(IL, ELIGIBLE_REPAYMENT, 0),
            wage_cut=np.where(OH_COMPARABLE, ELIGIBLE_REPAYMENT, 0),
        ),
        OUTPUTS,
    )
    yield out
    gc.collect()


def assert_relief(r, reference, rows):
    """Illinois tax and Ohio taxable income in `r` equal `reference` on `rows`."""
    np.testing.assert_allclose(
        r["il_income_tax"][IL & rows],
        reference["il_income_tax"][IL & rows],
        atol=TOLERANCE,
    )
    oh_rows = OH_COMPARABLE & rows
    np.testing.assert_allclose(
        r["oh_taxable_income"][oh_rows],
        reference["oh_taxable_income"][oh_rows],
        atol=TOLERANCE,
    )


def test_each_federal_method_matches_the_existing_input_path(results):
    every = np.ones_like(REPAYMENT, dtype=bool)
    assert_relief(results["credit"], results["reference"], every)
    assert_relief(results["deduction_itemizing"], results["reference"], every)
    # The standard deduction under the deduction method claims nothing.
    np.testing.assert_allclose(
        results["deduction_standard"]["il_income_tax"][IL],
        results["none"]["il_income_tax"][IL],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        results["deduction_standard"]["oh_taxable_income"][OH],
        results["none"]["oh_taxable_income"][OH],
        atol=TOLERANCE,
    )


def test_eligible_returns_get_relief_when_the_earlier_tax_fell(results):
    eligible = REPAYMENT > THRESHOLD
    assert_relief(results["model"], results["reference"], eligible & (DECREASE > 0))
    assert_relief(results["model"], results["none"], ~eligible)


def test_state_tax_never_rises(results):
    with_repayment = results["model"]["state_income_tax"]
    without = results["none"]["state_income_tax"]
    assert np.all(with_repayment <= without + TOLERANCE)
    assert np.any(with_repayment < without - 1), "some repayment should lower tax"
    table = with_repayment.reshape(SHAPE)
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the repayment"
