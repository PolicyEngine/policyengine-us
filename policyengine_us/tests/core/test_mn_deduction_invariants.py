"""Check federal compatibility and Minnesota bounds across generated returns.

Each batch includes all filing statuses. Joint returns contain two adult
filers; generated person amounts belong to the head, and spouses receive zero.
Separate simulations preserve input and cache isolation across policy years.
"""

import numpy as np
from hypothesis import example, given, settings, strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.itemizing.charitable_deduction import (
    compute_charitable_deduction,
)


SYSTEM = CountryTaxBenefitSystem()
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
PROPERTY_SETTINGS = settings(
    max_examples=8,
    deadline=None,
    database=None,
    derandomize=True,
)


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
    return Simulation(tax_benefit_system=SYSTEM, situation=situation)


def set_tax_unit_amounts(simulation, variable, year, values):
    """Assign person inputs to heads while preserving each tax unit's total."""
    if SYSTEM.variables[variable].entity.key == "person":
        unit = simulation.populations["tax_unit"].members_entity_id
        head = simulation.calculate("is_tax_unit_head", year)
        values = np.asarray(values)[unit] * head
    simulation.set_input(variable, year, values)


def assert_amounts(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=0.1)


@PROPERTY_SETTINGS
@example(
    agi=100_000,
    donations=(10_000, 5_000, 20_000, 5_000, 15_000, 10_000),
)
@given(
    agi=st.integers(min_value=0, max_value=1_000_000),
    donations=st.tuples(*[st.integers(0, 1_000_000)] * 6),
)
def test_federal_charitable_extraction_preserves_existing_results(agi, donations):
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


@PROPERTY_SETTINGS
@example(agi=100_000, contribution=750, increase=1_000)
@given(
    agi=st.integers(min_value=0, max_value=1_000_000),
    contribution=st.integers(min_value=0, max_value=500_000),
    increase=st.integers(min_value=0, max_value=500_000),
)
def test_minnesota_charity_bounds_monotonicity_and_consumers(
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


@PROPERTY_SETTINGS
@example(real=15_000, personal=2_000, increase=5_000, historical=10_000)
@given(
    real=st.integers(min_value=0, max_value=100_000),
    personal=st.integers(min_value=0, max_value=100_000),
    increase=st.integers(min_value=0, max_value=100_000),
    historical=st.integers(min_value=0, max_value=100_000),
)
def test_minnesota_property_cap_bounds_statuses_and_historical_compatibility(
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
