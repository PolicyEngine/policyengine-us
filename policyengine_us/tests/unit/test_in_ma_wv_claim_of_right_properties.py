"""Properties of Indiana's, Massachusetts's and West Virginia's claim of right relief.

Indiana (IC 6-3-1-3.5(a)(22)), Massachusetts (M.G.L. c. 62, s. 3(B)(a)(14))
and West Virginia (Schedule M, IRC 1341 Repayments) take a repayment of income
held under a claim of right off the state base whichever federal method
applies. Indiana and Massachusetts take any amount; West Virginia only
repayments over $3,000. The policy cases are in YAML. The federal method and
itemizing choice come from federal branch computations, so these tests check
over a grid, with independent simulations:

- each state's income tax is the same whether the federal credit method, the
  deduction method with itemizing, or the deduction method with the standard
  deduction is fixed, and equals the model's own choice;
- the deduction lowers the state base dollar for dollar: Indiana and West
  Virginia AGI by the repayment (West Virginia's only above $3,000), and
  Massachusetts Part B income until it reaches zero;
- Indiana income tax equals that of a simulation with no repayment and the
  same amount entered through the existing in_other_deductions input;
- no state's income tax ever rises with a repayment, or as the repayment
  grows.
"""

import gc
import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
STATES = ["IN", "MA", "WV"]
REPAYMENTS = [0, 2_000, 3_000, 3_001, 10_000, 60_000]
WAGES = [20_000, 80_000, 300_000]
CHARITY = [0, 30_000]
AXES = [STATES, REPAYMENTS, WAGES, CHARITY]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
STATE = np.array([point[0] for point in GRID])
REPAYMENT, WAGE, CHARITABLE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(1, len(AXES))
)
ZEROS = np.zeros_like(REPAYMENT)
IN, MA, WV = (STATE == state for state in STATES)
THRESHOLD = 3_000
DECREASE = 2_500
TOLERANCE = 0.01
# Federal method and itemizing choice fixed as inputs.
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
VARIABLES = [
    "state_income_tax",
    "in_claim_of_right_deduction",
    "in_agi",
    "ma_claim_of_right_deduction",
    "ma_part_b_taxable_income_before_exemption",
    "wv_claim_of_right_subtraction",
    "wv_agi",
]


def grid_simulation(repayment, tax_unit_inputs=None, in_other_deductions=ZEROS):
    """One single-person tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {YEAR: 40},
            "employment_income": {YEAR: WAGE[i]},
            "charitable_cash_donations": {YEAR: CHARITABLE[i]},
            "claim_of_right_repayment": {YEAR: float(repayment[i])},
        }
        tax_unit = {
            "members": [person],
            "claim_of_right_prior_year_tax_decrease": {YEAR: DECREASE},
            "in_other_deductions": {YEAR: float(in_other_deductions[i])},
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


@pytest.fixture(scope="module")
def results():
    out = {"model": calculate(grid_simulation(REPAYMENT), VARIABLES)}
    for name, inputs in METHODS.items():
        out[name] = calculate(grid_simulation(REPAYMENT, inputs), ["state_income_tax"])
    out["none"] = calculate(grid_simulation(ZEROS), VARIABLES)
    # Independent reference for Indiana: no repayment, and the same amount
    # entered through the input that existed before this deduction.
    out["reference"] = calculate(
        grid_simulation(ZEROS, in_other_deductions=np.where(IN, REPAYMENT, 0)),
        ["state_income_tax"],
    )
    yield out
    gc.collect()


def test_state_tax_does_not_depend_on_the_federal_method(results):
    model = results["model"]["state_income_tax"]
    for name in METHODS:
        np.testing.assert_allclose(
            results[name]["state_income_tax"], model, atol=TOLERANCE, err_msg=name
        )


def test_deductions_by_state(results):
    r = results["model"]
    np.testing.assert_allclose(
        r["in_claim_of_right_deduction"], np.where(IN, REPAYMENT, 0)
    )
    np.testing.assert_allclose(
        r["ma_claim_of_right_deduction"], np.where(MA, REPAYMENT, 0)
    )
    np.testing.assert_allclose(
        r["wv_claim_of_right_subtraction"],
        np.where(WV & (REPAYMENT > THRESHOLD), REPAYMENT, 0),
    )


def test_bases_fall_dollar_for_dollar(results):
    r, none = results["model"], results["none"]
    np.testing.assert_allclose(
        (none["in_agi"] - r["in_agi"])[IN], REPAYMENT[IN], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        (none["wv_agi"] - r["wv_agi"])[WV],
        np.where(REPAYMENT > THRESHOLD, REPAYMENT, 0)[WV],
        atol=TOLERANCE,
    )
    base = none["ma_part_b_taxable_income_before_exemption"]
    np.testing.assert_allclose(
        (base - r["ma_part_b_taxable_income_before_exemption"])[MA],
        np.minimum(REPAYMENT, base)[MA],
        atol=TOLERANCE,
    )


def test_indiana_matches_the_existing_input_path(results):
    np.testing.assert_allclose(
        results["model"]["state_income_tax"][IN],
        results["reference"]["state_income_tax"][IN],
        atol=TOLERANCE,
    )


def test_state_tax_never_rises(results):
    with_repayment = results["model"]["state_income_tax"]
    without = results["none"]["state_income_tax"]
    assert np.all(with_repayment <= without + TOLERANCE)
    for state in [IN, MA]:
        small = state & (REPAYMENT == 2_000)
        assert np.all(with_repayment[small] < without[small] - 1), (
            "Indiana and Massachusetts deduct repayments of $3,000 or less"
        )
    table = with_repayment.reshape(SHAPE)
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the repayment"
