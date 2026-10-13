"""Properties of New Jersey's claim of right repayment offset.

N.J.S.A. 54A:5-2 and TAM 2011-7: a repayment is applied against income of the
same category in the year of repayment, and a category left negative is
reported as zero. New Jersey has no counterpart to the section 1341 credit.
The policy cases are in YAML. These tests check what YAML cannot: over a grid
of single and joint returns, under and over the pension exclusion's age, that
a repayment acts on New Jersey AGI and taxable income exactly as a simulation
with no repayment and that much less income in the repaid category, which also
reaches the pension exclusion (line 20a) and Worksheet D's earnings test (line
15); that no spouse's offset exceeds their own income in the category; that
New Jersey tax does not depend on the federal method and never rises with a
repayment or as it grows; and that each category's sources are New Jersey
gross income sources.
"""

import gc
import itertools

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2025
CATEGORIES = ["WAGES", "PENSIONS_AND_ANNUITIES", "NOT_TAXED", "OTHER"]
REPAYMENTS = [0, 1_000, 8_000, 60_000]
HEAD_WAGES = [0, 2_000, 50_000]
HEAD_PENSIONS = [0, 20_000]
AGES = [40, 70]
# None is a single return; a number is a joint return with that spouse's wages.
SPOUSE_WAGES = [None, 30_000]
AXES = [CATEGORIES, REPAYMENTS, HEAD_WAGES, HEAD_PENSIONS, AGES, SPOUSE_WAGES]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
CATEGORY = np.array([point[0] for point in GRID])
REPAYMENT, WAGE, PENSION, AGE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(1, 5)
)
JOINT = np.array([point[5] is not None for point in GRID])
SPOUSE_WAGE = np.array([point[5] or 0 for point in GRID], dtype=float)
ZEROS = np.zeros_like(REPAYMENT)
TOLERANCE = 0.01


def category_cuts():
    """The income each filer gives up in the reference: the return's offset,
    min(repayment, the filers' income in the repaid category), taken from the
    head first. Any split gives the same return totals here, since both
    spouses are the same age."""
    wages = CATEGORY == "WAGES"
    pensions = CATEGORY == "PENSIONS_AND_ANNUITIES"
    category_income = np.where(
        wages, WAGE + SPOUSE_WAGE, np.where(pensions, PENSION, 0)
    )
    offset = np.minimum(REPAYMENT, category_income)
    head_income = np.where(wages, WAGE, np.where(pensions, PENSION, 0))
    head_cut = np.minimum(offset, head_income)
    return offset, head_cut, offset - head_cut


OFFSET, HEAD_CUT, SPOUSE_CUT = category_cuts()


def grid_simulation(repayment, cut=False, tax_unit_inputs=None):
    """One New Jersey return per grid point; the head repays. With cut=True,
    no repayment and each filer's repaid-category income lowered instead."""
    situation = {"people": {}, "tax_units": {}, "marital_units": {}, "households": {}}
    for i in range(len(GRID)):
        head_wages = WAGE[i] - (HEAD_CUT[i] if cut and CATEGORY[i] == "WAGES" else 0)
        head_pension = PENSION[i] - (
            HEAD_CUT[i] if cut and CATEGORY[i] == "PENSIONS_AND_ANNUITIES" else 0
        )
        head = f"h{i}"
        members = [head]
        situation["people"][head] = {
            "age": {YEAR: AGE[i]},
            "employment_income": {YEAR: head_wages},
            "taxable_pension_income": {YEAR: head_pension},
            "taxable_interest_income": {YEAR: 1_000},
            "claim_of_right_repayment": {YEAR: 0 if cut else float(repayment[i])},
            "nj_claim_of_right_repayment_category": {YEAR: CATEGORY[i]},
        }
        if JOINT[i]:
            spouse = f"s{i}"
            members.append(spouse)
            situation["people"][spouse] = {
                "age": {YEAR: AGE[i]},
                "employment_income": {
                    YEAR: SPOUSE_WAGE[i] - (SPOUSE_CUT[i] if cut else 0)
                },
            }
        # Lowering wages in the reference can qualify a couple over 65 for a
        # Medicare Savings Program, which pays their Part B premiums and so
        # removes New Jersey's medical expense deduction; the repayment itself
        # does not. Pin the deduction so the comparison isolates the offset.
        tax_unit = {"members": members, "nj_medical_expense_deduction": {YEAR: 0}}
        for name, value in (tax_unit_inputs or {}).items():
            tax_unit[name] = {YEAR: value}
        situation["tax_units"][f"t{i}"] = tax_unit
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
        "nj_taxable_income": by_tax_unit(model, "nj_taxable_income"),
        "tax": by_tax_unit(model, "nj_income_tax"),
        "person_offset": np.asarray(model.calculate("nj_claim_of_right_offset", YEAR)),
        "person_wages": np.asarray(model.calculate("employment_income", YEAR)),
        "person_pension": np.asarray(model.calculate("taxable_pension_income", YEAR)),
    }
    reference = grid_simulation(ZEROS, cut=True)
    out["reference_nj_agi"] = by_tax_unit(reference, "nj_agi")
    out["reference_nj_taxable_income"] = by_tax_unit(reference, "nj_taxable_income")
    out["tax_none"] = by_tax_unit(grid_simulation(ZEROS), "nj_income_tax")
    out["tax_federal_credit"] = by_tax_unit(
        grid_simulation(
            REPAYMENT, tax_unit_inputs={"claim_of_right_credit_applies": True}
        ),
        "nj_income_tax",
    )
    yield out
    gc.collect()


def test_a_repayment_acts_as_less_income_in_its_category(results):
    np.testing.assert_allclose(results["offset"], OFFSET, atol=TOLERANCE)
    np.testing.assert_allclose(
        results["nj_agi"], results["reference_nj_agi"], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        results["nj_taxable_income"],
        results["reference_nj_taxable_income"],
        atol=TOLERANCE,
    )
    assert np.any((OFFSET > 0) & (OFFSET < REPAYMENT)), "the cap should bind"


def test_no_spouse_offsets_more_than_their_own_category_income(results):
    # In the simulation's person order: each head, then its spouse.
    bound = []
    for i in range(len(GRID)):
        own = {"WAGES": WAGE[i], "PENSIONS_AND_ANNUITIES": PENSION[i]}
        bound.append(own.get(CATEGORY[i], 0))
        if JOINT[i]:
            bound.append(SPOUSE_WAGE[i] if CATEGORY[i] == "WAGES" else 0)
    offset = results["person_offset"]
    assert np.all(offset >= -TOLERANCE)
    assert np.all(offset <= np.array(bound) + TOLERANCE)


def test_tax_ignores_the_federal_method_and_never_rises(results):
    np.testing.assert_allclose(
        results["tax_federal_credit"], results["tax"], atol=TOLERANCE
    )
    assert np.all(results["tax"] <= results["tax_none"] + TOLERANCE)
    assert np.any(results["tax"] < results["tax_none"] - 1)
    table = results["tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the repayment"


def test_category_sources_are_gross_income_sources():
    non_negative = system.parameters(YEAR).gov.states.nj.tax.income.gross_income
    allowed = set(non_negative.non_negative_sources)
    p = non_negative.claim_of_right_category_sources
    for name in [
        "wages",
        "interest",
        "dividends",
        "gambling_winnings",
        "pensions_and_annuities",
        "alimony",
    ]:
        sources = set(getattr(p, name))
        assert sources and sources <= allowed, (name, sources - allowed)
