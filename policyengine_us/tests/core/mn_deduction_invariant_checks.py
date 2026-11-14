"""Run generated deduction invariants in one small, isolated Core model.

The pytest client sends inputs to this worker. A fresh process installs a
package-path proxy before importing production modules, avoiding country model
startup without changing the parent interpreter's package state. The worker
loads actual variable classes and three actual parameter subtrees; explicit
inputs isolate upstream branches outside these checks. Published parameter
entries cover the years under test, and zero AGI makes regular deduction
reduction thresholds irrelevant. Country preprocessing and uprating stay out
of scope; YAML cases exercise country integration.
"""

import contextlib
import importlib.machinery
import json
from pathlib import Path
import sys
import traceback
from types import ModuleType


def initialize():
    global np, ParameterNode, Simulation, TaxBenefitSystem, entities
    global compute_charitable_deduction, create_in_state_variable, SYSTEM
    if "policyengine_us" in sys.modules:
        raise RuntimeError("The invariant worker must precede country imports")
    package = ModuleType("policyengine_us")
    package.__path__ = [str(COUNTRY_DIR)]
    package.__package__ = "policyengine_us"
    package.__file__ = str(COUNTRY_DIR / "__init__.py")
    package.__spec__ = importlib.machinery.ModuleSpec(
        "policyengine_us", loader=None, is_package=True
    )
    package.__spec__.submodule_search_locations = package.__path__
    sys.modules["policyengine_us"] = package

    import numpy as np
    from policyengine_core.parameters import ParameterNode
    from policyengine_core.simulations import Simulation
    from policyengine_core.taxbenefitsystems import TaxBenefitSystem
    from policyengine_us.entities import entities
    from policyengine_us.variables.gov.irs.income.taxable_income.deductions.itemizing.charitable_deduction import (
        compute_charitable_deduction,
    )
    from policyengine_us.variables.household.demographic.geographic.state.in_state import (
        create_in_state_variable,
    )

    SYSTEM = make_system()


STATUSES = [
    "SINGLE",
    "SEPARATE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
]


DONATION_INPUTS = [
    "resolved_charitable_cash_donations_50_pct",
    "resolved_charitable_cash_donations_non_50_pct",
    "resolved_charitable_non_cash_donations_50_pct",
    "resolved_charitable_non_cash_donations_non_50_pct",
    "resolved_charitable_capital_gain_donations_50_pct",
    "resolved_charitable_capital_gain_donations_non_50_pct",
]


COUNTRY_DIR = Path(__file__).parents[2]


IRS_TAXABLE_INCOME = "gov/irs/income/taxable_income"


MN_INCOME_TAX = "gov/states/mn/tax/income"


VARIABLE_FILES = [
    "household/demographic/age/age.py",
    "household/demographic/geographic/state_code.py",
    "household/demographic/geographic/state_code_str.py",
    "household/demographic/tax_unit/filing_status.py",
    "household/demographic/tax_unit/is_tax_unit_head.py",
    "household/demographic/tax_unit/is_tax_unit_spouse.py",
    "household/demographic/tax_unit/is_tax_unit_dependent.py",
    "household/expense/tax/real_estate_taxes.py",
    "household/expense/person/investment_interest_expense.py",
    "household/income/tax_unit/us_govt_interest.py",
    *[f"household/expense/charitable/{name}.py" for name in DONATION_INPUTS],
    f"{IRS_TAXABLE_INCOME}/adjusted_gross_income/adjusted_gross_income.py",
    f"{IRS_TAXABLE_INCOME}/adjusted_gross_income/positive_agi.py",
    f"{IRS_TAXABLE_INCOME}/adjusted_gross_income/above_the_line_deductions/charitable_contributions/charitable_contributions_ald.py",
    f"{IRS_TAXABLE_INCOME}/deductions/itemized_deductions_less_salt.py",
    f"{IRS_TAXABLE_INCOME}/deductions/capped_property_taxes.py",
    *[
        f"{IRS_TAXABLE_INCOME}/deductions/itemizing/{name}.py"
        for name in [
            "charitable_deduction",
            "charitable_deduction_before_floor",
            "medical_expense_deduction",
            "casualty_loss_deduction",
            "misc_deduction",
            "deductible_mortgage_insurance_premiums",
        ]
    ],
    *[
        f"{MN_INCOME_TAX}/deductions/{name}.py"
        for name in [
            "mn_charitable_deduction",
            "mn_property_tax_deduction",
            "mn_personal_property_taxes",
            "mn_itemized_deductions",
            "mn_casualty_loss_deduction",
            "mn_itemizing",
        ]
    ],
    *[
        f"{MN_INCOME_TAX}/subtractions/{name}.py"
        for name in [
            "mn_charity_subtraction",
            "mn_social_security_subtraction",
            "mn_military_pension_subtraction",
        ]
    ],
    f"{MN_INCOME_TAX}/amt/mn_amt_taxable_income.py",
]


PARAMETER_SUBTREES = [
    "gov.irs.deductions.itemized.charity",
    "gov.states.mn.tax.income.deductions.itemized",
    "gov.states.mn.tax.income.subtractions.charity",
]


ZERO_INPUTS = [
    "adjusted_gross_income",
    "itemized_deductions_less_salt",
    "medical_expense_deduction",
    "investment_interest_expense",
    "capped_property_taxes",
    "real_estate_taxes",
    "mn_personal_property_taxes",
    "casualty_loss_deduction",
    "mn_casualty_loss_deduction",
    "deductible_mortgage_insurance_premiums",
    "charitable_contributions_ald",
    "misc_deduction",
    "us_govt_interest",
    "mn_social_security_subtraction",
    "mn_military_pension_subtraction",
    "mn_itemizing",
]


def make_system():
    system = TaxBenefitSystem(entities)
    for relative_path in VARIABLE_FILES:
        system.add_variables_from_file(str(COUNTRY_DIR / "variables" / relative_path))
    system.add_variable(create_in_state_variable("MN"))
    root = ParameterNode("", data={})
    for subtree in PARAMETER_SUBTREES:
        parent = root
        parts = subtree.split(".")
        for index, name in enumerate(parts[:-1]):
            if name not in parent.children:
                parent.add_child(
                    name, ParameterNode(".".join(parts[: index + 1]), data={})
                )
            parent = parent.children[name]
        parent.add_child(
            parts[-1],
            ParameterNode(
                subtree,
                directory_path=str(COUNTRY_DIR / "parameters" / Path(*parts)),
            ),
        )
    system.parameters = root
    return system


def make_simulation(year, statuses, states=None):
    period = str(year)
    states = states or ["MN"] * len(statuses)
    situation = {
        "people": {},
        "tax_units": {},
        "families": {},
        "marital_units": {},
        "spm_units": {},
        "households": {},
    }
    for index, (status, state) in enumerate(zip(statuses, states)):
        person = f"person_{index}"
        situation["people"][person] = {
            "age": {period: 40},
            "is_tax_unit_head": {period: True},
            "is_tax_unit_spouse": {period: False},
            "is_tax_unit_dependent": {period: False},
        }
        members = [person]
        if status == "JOINT":
            spouse = f"spouse_{index}"
            situation["people"][spouse] = {
                "age": {period: 40},
                "is_tax_unit_head": {period: False},
                "is_tax_unit_spouse": {period: True},
                "is_tax_unit_dependent": {period: False},
            }
            members.append(spouse)
        for entity in ["tax_units", "families", "marital_units", "spm_units"]:
            situation[entity][str(index)] = {"members": members}
        situation["tax_units"][str(index)]["filing_status"] = {period: status}
        situation["households"][str(index)] = {
            "members": members,
            "state_code": {period: state},
        }
    simulation = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    for variable in ZERO_INPUTS:
        set_tax_unit_amounts(simulation, variable, year, np.zeros(len(statuses)))
    return simulation


def set_tax_unit_amounts(simulation, variable, year, values):
    """Assign person inputs to heads while preserving each tax unit's total."""
    if SYSTEM.variables[variable].entity.key == "person":
        unit = simulation.populations["tax_unit"].members_entity_id
        head = simulation.calculate("is_tax_unit_head", year)
        values = np.asarray(values)[unit] * head
    simulation.set_input(variable, year, values)


def assert_amounts(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=0.1)


def check_federal_charitable_extraction_preserves_existing_results(agi, donations):
    # Exercise each federal ceiling regime and retain the existing helper as the oracle.
    amounts = (
        np.asarray(donations, dtype=np.float32)[None, :]
        * np.array([0, 0.25, 0.5, 1, 2], dtype=np.float32)[:, None]
    )
    agi_values = np.full(5, agi, dtype=np.float32)
    for year in [2013, 2018, 2020, 2021, 2024, 2025, 2026]:
        sim = make_simulation(year, STATUSES, ["CA", "MN", "NY", "MN", "TX"])
        set_tax_unit_amounts(sim, "positive_agi", year, agi_values)
        for column, variable in enumerate(DONATION_INPUTS):
            set_tax_unit_amounts(sim, variable, year, amounts[:, column])
        # Core's bincount sums stored Person amounts into float64 tax-unit totals.
        unit = sim.populations["tax_unit"].members_entity_id
        totals = np.column_stack(
            [
                np.bincount(
                    unit,
                    weights=sim.calculate(variable, year),
                    minlength=len(STATUSES),
                )
                for variable in DONATION_INPUTS
            ]
        )
        p = SYSTEM.parameters(str(year)).gov.irs.deductions.itemized.charity
        before_floor = compute_charitable_deduction(
            cash_50=totals[:, 0],
            cash_non_50=totals[:, 1],
            ordinary_50=totals[:, 2],
            ordinary_non_50=totals[:, 3],
            cg_50=totals[:, 4],
            cg_non_50=totals[:, 5],
            positive_agi=agi_values,
            ceiling_all=p.ceiling.all,
            ceiling_non_cash=p.ceiling.non_cash,
            ceiling_non_50=p.ceiling.non_cash_to_non_50_pct_org,
            ceiling_cg_50=p.ceiling.capital_gain_to_50_pct_org,
            ceiling_cg_non_50=p.ceiling.capital_gain_to_non_50_pct_org,
            non_50_pct_cash_add_back=p.ceiling.non_50_pct_cash_add_back,
            qualified_cash_election=p.qualified_cash_election,
        )
        expected = (
            np.maximum(0, before_floor - p.floor.amount * agi_values)
            if p.floor.applies
            else before_floor
        )
        np.testing.assert_array_equal(
            sim.calculate("charitable_deduction_before_floor", year),
            np.asarray(before_floor, dtype=np.float32),
        )
        np.testing.assert_array_equal(
            sim.calculate("charitable_deduction", year),
            np.asarray(expected, dtype=np.float32),
        )


def check_minnesota_charity_bounds_monotonicity_and_consumers(
    agi, contribution, increase
):
    before_floor = np.tile([contribution, contribution + increase], len(STATUSES))
    statuses = [status for status in STATUSES for _ in range(2)]
    itemizing = np.tile([False, True], len(STATUSES))
    for year in [2024, 2025, 2026]:
        sim = make_simulation(year, statuses)
        federal = (
            np.maximum(0, before_floor - 0.005 * agi)
            if year >= 2026
            else before_floor / 2
        )
        # Historical callers must preserve a supplied federal deduction.
        set_tax_unit_amounts(sim, "charitable_deduction", year, federal)
        set_tax_unit_amounts(
            sim, "charitable_deduction_before_floor", year, before_floor
        )
        set_tax_unit_amounts(sim, "positive_agi", year, np.full(10, agi))
        set_tax_unit_amounts(sim, "mn_itemizing", year, itemizing)
        set_tax_unit_amounts(
            sim, "itemized_deductions_less_salt", year, federal + 1_000
        )
        # Isolate the charity substitution from Minnesota's income reductions.
        set_tax_unit_amounts(sim, "adjusted_gross_income", year, np.zeros(10))
        set_tax_unit_amounts(sim, "capped_property_taxes", year, np.zeros(10))
        set_tax_unit_amounts(sim, "real_estate_taxes", year, np.zeros(10))
        set_tax_unit_amounts(sim, "mn_personal_property_taxes", year, np.zeros(10))
        set_tax_unit_amounts(sim, "casualty_loss_deduction", year, np.zeros(10))
        set_tax_unit_amounts(sim, "mn_casualty_loss_deduction", year, np.zeros(10))
        p = SYSTEM.parameters(str(year)).gov.states.mn.tax.income
        for variable in p.deductions.itemized.disallowed_interest_components:
            set_tax_unit_amounts(sim, variable, year, np.zeros(10))
        expected = np.maximum(0, before_floor - 0.01 * agi) if year >= 2026 else federal
        deduction = sim.calculate("mn_charitable_deduction", year)
        assert_amounts(deduction, expected)
        assert np.all(deduction >= 0)
        assert np.all(deduction <= before_floor + 0.1)
        assert np.all(deduction[1::2] >= deduction[::2] - 0.1)
        if year >= 2026:
            assert np.all(deduction <= federal + 0.1)
        assert_amounts(sim.calculate("mn_itemized_deductions", year), expected + 1_000)
        subtraction = p.subtractions.charity.fraction * np.maximum(
            0, expected - p.subtractions.charity.threshold
        )
        assert_amounts(
            sim.calculate("mn_charity_subtraction", year),
            np.where(itemizing, 0, subtraction),
        )


def check_minnesota_property_cap_bounds_statuses_and_historical_compatibility(
    real, personal, increase, historical
):
    statuses = [status for status in STATUSES for _ in range(3)]
    real_taxes = np.tile([real, personal, real + increase], len(STATUSES))
    personal_taxes = np.tile([personal, real, personal], len(STATUSES))
    limits = np.repeat([10_000, 5_000, 10_000, 10_000, 10_000], 3)
    for year in [2024, 2025, 2026]:
        sim = make_simulation(year, statuses)
        set_tax_unit_amounts(sim, "real_estate_taxes", year, real_taxes)
        set_tax_unit_amounts(sim, "mn_personal_property_taxes", year, personal_taxes)
        set_tax_unit_amounts(
            sim, "capped_property_taxes", year, np.full(15, historical)
        )
        set_tax_unit_amounts(sim, "itemized_deductions_less_salt", year, np.zeros(15))
        set_tax_unit_amounts(sim, "charitable_deduction", year, np.zeros(15))
        set_tax_unit_amounts(
            sim, "charitable_deduction_before_floor", year, np.zeros(15)
        )
        set_tax_unit_amounts(sim, "casualty_loss_deduction", year, np.zeros(15))
        set_tax_unit_amounts(sim, "mn_casualty_loss_deduction", year, np.zeros(15))
        set_tax_unit_amounts(sim, "adjusted_gross_income", year, np.zeros(15))
        p = SYSTEM.parameters(str(year)).gov.states.mn.tax.income.deductions.itemized
        for variable in p.disallowed_interest_components:
            set_tax_unit_amounts(sim, variable, year, np.zeros(15))
        expected = (
            np.minimum(real_taxes + personal_taxes, limits)
            if year >= 2025
            else np.full(15, historical)
        )
        deduction = sim.calculate("mn_property_tax_deduction", year)
        assert_amounts(deduction, expected)
        assert_amounts(sim.calculate("mn_itemized_deductions", year), expected)
        assert np.all(deduction >= 0)
        assert_amounts(deduction[::3], deduction[1::3])
        assert np.all(deduction[2::3] >= deduction[::3] - 0.1)
        if year >= 2025:
            assert np.all(deduction <= limits)
            assert np.all(deduction <= real_taxes + personal_taxes + 0.1)


def check_minnesota_amt_preserves_federal_charitable_deduction(agi, contribution):
    year = 2026
    sim = make_simulation(year, STATUSES)
    agi_values = np.full(len(STATUSES), agi, dtype=np.float32)
    # Bound cash contributions by 60% of AGI before either charitable floor.
    allowed = min(contribution, 0.6 * agi)
    before_floor = np.asarray(
        [allowed * share for share in [0, 0.25, 0.5, 0.75, 1]],
        dtype=np.float32,
    )
    federal = np.maximum(0, before_floor - 0.005 * agi_values)
    set_tax_unit_amounts(sim, "adjusted_gross_income", year, agi_values)
    set_tax_unit_amounts(sim, "positive_agi", year, agi_values)
    set_tax_unit_amounts(sim, "charitable_deduction_before_floor", year, before_floor)
    set_tax_unit_amounts(sim, "charitable_deduction", year, federal)
    set_tax_unit_amounts(sim, "mn_itemizing", year, np.ones(len(STATUSES), dtype=bool))
    set_tax_unit_amounts(sim, "mn_charity_subtraction", year, np.zeros(len(STATUSES)))
    np.testing.assert_array_equal(
        sim.calculate("mn_amt_taxable_income", year),
        np.asarray(agi_values - federal, dtype=np.float32),
    )


CHECKS = {
    "federal": check_federal_charitable_extraction_preserves_existing_results,
    "charity": check_minnesota_charity_bounds_monotonicity_and_consumers,
    "property": check_minnesota_property_cap_bounds_statuses_and_historical_compatibility,
    "amt": check_minnesota_amt_preserves_federal_charitable_deduction,
}


def main():
    protocol_stdout = sys.stdout

    def reply(value):
        protocol_stdout.write(json.dumps(value, allow_nan=False) + "\n")
        protocol_stdout.flush()

    try:
        with contextlib.redirect_stdout(sys.stderr):
            initialize()
    except Exception:
        reply({"status": "error", "traceback": traceback.format_exc()})
        return 1
    reply({"status": "ready"})
    for line in sys.stdin:
        try:
            request = json.loads(line)
            with contextlib.redirect_stdout(sys.stderr):
                CHECKS[request["check"]](**request["arguments"])
            response = {"status": "passed"}
        except AssertionError:
            response = {"status": "failed", "traceback": traceback.format_exc()}
        except Exception:
            response = {"status": "error", "traceback": traceback.format_exc()}
        reply(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
