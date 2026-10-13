"""Properties of New Jersey's claim of right repayment offset.

N.J.S.A. 54A:5-2 and TAM 2011-7: a repayment is applied against income of the
same category in the year of repayment, and a category with a net negative
amount is reported as zero. New Jersey has no counterpart to the section 1341
credit. The policy cases are in YAML; these tests check over a grid of single
and joint returns, against a reference computed here from the inputs and
against independent simulations:

- the return's offset is the smaller of the repayment and the filers' income
  in the repaid category (zero for income New Jersey did not tax), and New
  Jersey AGI falls by exactly that amount;
- no spouse's offset exceeds their own income in the category;
- New Jersey income tax is the same under every federal method and itemizing
  choice, never rises with a repayment, and never rises as it grows.
"""

import gc
import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
CATEGORIES = ["WAGES", "PENSIONS_AND_ANNUITIES", "NOT_TAXED"]
REPAYMENTS = [0, 1_000, 8_000, 60_000]
HEAD_WAGES = [0, 5_000, 50_000]
HEAD_PENSIONS = [0, 20_000]
# None is a single return; a number is a joint return with that spouse's wages.
SPOUSE_WAGES = [None, 0, 30_000]
AXES = [CATEGORIES, REPAYMENTS, HEAD_WAGES, HEAD_PENSIONS, SPOUSE_WAGES]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
CATEGORY = np.array([point[0] for point in GRID])
REPAYMENT, WAGE, PENSION = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(1, 4)
)
JOINT = np.array([point[4] is not None for point in GRID])
SPOUSE_WAGE = np.array([point[4] or 0 for point in GRID], dtype=float)
ZEROS = np.zeros_like(REPAYMENT)
TOLERANCE = 0.01
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


def grid_simulation(repayment, tax_unit_inputs=None):
    """One New Jersey return per grid point; the head repays."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, (category, *_rest) in enumerate(GRID):
        head = f"h{i}"
        members = [head]
        situation["people"][head] = {
            "age": {YEAR: 40},
            "employment_income": {YEAR: WAGE[i]},
            "taxable_pension_income": {YEAR: PENSION[i]},
            "claim_of_right_repayment": {YEAR: float(repayment[i])},
            "nj_claim_of_right_repayment_category": {YEAR: category},
        }
        if JOINT[i]:
            spouse = f"s{i}"
            members.append(spouse)
            situation["people"][spouse] = {
                "age": {YEAR: 40},
                "employment_income": {YEAR: SPOUSE_WAGE[i]},
            }
        tax_unit = {"members": members}
        for name, value in (tax_unit_inputs or {}).items():
            tax_unit[name] = {YEAR: value}
        situation["tax_units"][f"t{i}"] = tax_unit
        situation["marital_units"] = situation.get("marital_units", {})
        situation["marital_units"][f"m{i}"] = {"members": members}
        situation["households"][f"hh{i}"] = {
            "members": members,
            "state_code": {YEAR: "NJ"},
        }
    return Simulation(situation=situation)


def by_tax_unit(simulation, variable):
    return np.asarray(simulation.calculate(variable, YEAR, map_to="tax_unit"))


@pytest.fixture(scope="module")
def results():
    model = grid_simulation(REPAYMENT)
    out = {
        "offset": by_tax_unit(model, "nj_claim_of_right_offset"),
        "nj_agi": by_tax_unit(model, "nj_agi"),
        "tax": by_tax_unit(model, "nj_income_tax"),
        "person_offset": np.asarray(model.calculate("nj_claim_of_right_offset", YEAR)),
    }
    none = grid_simulation(ZEROS)
    out["nj_agi_none"] = by_tax_unit(none, "nj_agi")
    out["tax_none"] = by_tax_unit(none, "nj_income_tax")
    for name, inputs in METHODS.items():
        out[f"tax_{name}"] = by_tax_unit(
            grid_simulation(REPAYMENT, inputs), "nj_income_tax"
        )
    yield out
    gc.collect()


def expected_offset():
    category_income = np.select(
        [CATEGORY == "WAGES", CATEGORY == "PENSIONS_AND_ANNUITIES"],
        [WAGE + SPOUSE_WAGE, PENSION],
        0,
    )
    return np.minimum(REPAYMENT, category_income)


def test_offset_is_the_repayment_up_to_the_category_income(results):
    expected = expected_offset()
    np.testing.assert_allclose(results["offset"], expected, atol=TOLERANCE)
    np.testing.assert_allclose(
        results["nj_agi_none"] - results["nj_agi"], expected, atol=TOLERANCE
    )
    assert np.any((expected > 0) & (expected < REPAYMENT)), "the cap should bind"


def person_category_income():
    """Each filer's own income in the category the return's head repaid,
    in the simulation's person order (head, then spouse)."""
    income = []
    for i in range(len(GRID)):
        if CATEGORY[i] == "WAGES":
            income.append(WAGE[i])
        elif CATEGORY[i] == "PENSIONS_AND_ANNUITIES":
            income.append(PENSION[i])
        else:
            income.append(0)
        if JOINT[i]:
            income.append(SPOUSE_WAGE[i] if CATEGORY[i] == "WAGES" else 0)
    return np.array(income)


def test_no_spouse_offsets_more_than_their_own_category_income(results):
    offset = results["person_offset"]
    assert np.all(offset >= -TOLERANCE)
    assert np.all(offset <= person_category_income() + TOLERANCE)


def test_tax_does_not_depend_on_the_federal_method_and_never_rises(results):
    for name in METHODS:
        np.testing.assert_allclose(
            results[f"tax_{name}"], results["tax"], atol=TOLERANCE, err_msg=name
        )
    assert np.all(results["tax"] <= results["tax_none"] + TOLERANCE)
    assert np.any(results["tax"] < results["tax_none"] - 1)
    table = results["tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the repayment"
