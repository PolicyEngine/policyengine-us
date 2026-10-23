"""Montana's capped state-tax adjustment precedes the taxable-income floor.

MCA 15-30-2101(7) incorporates the subtraction-based federal definition of
taxable income. Form 2 Worksheet A reduces the deduction by the capped
state-income-tax adjustment before taxable income is floored at zero:
https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html
https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15

Generated batches exercise both federal deduction elections and excess
deductions, including Schedule 1-A from 2025. They check the ordering against
an independent reference and the former floor-then-add upper bound. Each
batch also includes the review's floor-binding witness and its higher-income
twin, where changing the order has no effect. Other Montana adjustments and
QBI are held at zero to isolate the state-tax adjustment.
"""

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEARS = (2024, 2025, 2026)


@pytest.fixture(scope="module")
def reference_system():
    # Reuse only the read-only policy source. Each generated batch gets its
    # own simulation, entities and calculation holders.
    return system


@st.composite
def deduction_case(draw):
    agi = draw(st.integers(min_value=-20_000, max_value=200_000))
    itemized = draw(st.integers(min_value=0, max_value=100_000))
    standard = draw(st.integers(min_value=0, max_value=40_000))
    # All of the generated state tax fits within the allowed itemized total.
    state_tax = draw(st.integers(min_value=0, max_value=min(itemized, 40_000)))
    itemizes = draw(st.booleans())
    schedule_1a = draw(st.integers(min_value=0, max_value=min(max(agi, 0), 10_000)))
    return agi, itemized, standard, state_tax, itemizes, schedule_1a


def _situation(points):
    people, tax_units, households = {}, {}, {}

    def all_years(value):
        return {year: value for year in YEARS}

    for index, (agi, itemized, standard, state_tax, itemizes, schedule_1a) in enumerate(
        points
    ):
        name = f"person_{index}"
        people[name] = {
            "age": all_years(40),
            "is_tax_unit_head": all_years(True),
            "real_estate_taxes": all_years(0),
            "mt_additions": all_years(0),
            "mt_subtractions": all_years(0),
            "mt_federal_obbba_subtraction": all_years(0),
        }
        tax_units[name] = {
            "members": [name],
            "adjusted_gross_income": all_years(agi),
            "exemptions": all_years(0),
            "tax_unit_itemizes": all_years(itemizes),
            "itemized_taxable_income_deductions": all_years(itemized),
            "standard_deduction": all_years(standard),
            "state_withheld_income_tax": all_years(state_tax),
            "local_income_tax": all_years(0),
            "state_sales_tax": all_years(0),
            "local_sales_tax": all_years(0),
            "salt_deduction": all_years(state_tax),
            "mt_federal_itemized_personal_property_taxes": all_years(0),
            "wagering_losses_deduction": all_years(0),
            "qualified_business_income_deduction": all_years(0),
            "charitable_deduction_for_non_itemizers": all_years(0),
            "tip_income_deduction": {
                year: schedule_1a if year >= 2025 else 0 for year in YEARS
            },
            "overtime_income_deduction": all_years(0),
            "additional_senior_deduction": all_years(0),
            "auto_loan_interest_deduction": all_years(0),
        }
        households[name] = {
            "members": [name],
            "state_code": all_years("MT"),
        }
    return {"people": people, "tax_units": tax_units, "households": households}


@settings(max_examples=6, deadline=None, derandomize=True)
@given(points=st.lists(deduction_case(), min_size=1, max_size=4))
def test_state_tax_adjustment_precedes_taxable_income_floor(reference_system, points):
    witnesses = [
        (10_000, 20_000, 14_600, 6_000, True, 0),
        (50_000, 20_000, 14_600, 6_000, True, 0),
    ]
    points = points + witnesses
    simulation = Simulation(
        tax_benefit_system=reference_system,
        situation=_situation(points),
    )
    agi, itemized, standard, state_tax, itemizes, schedule_1a = (
        np.asarray(values) for values in zip(*points)
    )
    adjustment = np.where(
        itemizes, np.minimum(state_tax, np.maximum(itemized - standard, 0)), 0
    )
    elected_deduction = np.where(itemizes, itemized, standard)

    for year in YEARS:
        federal_deductions = elected_deduction + (schedule_1a if year >= 2025 else 0)
        federal_pre_floor_base = agi - federal_deductions
        expected = np.maximum(federal_pre_floor_base + adjustment, 0)
        old_floor_then_add = np.maximum(federal_pre_floor_base, 0) + adjustment

        np.testing.assert_array_equal(
            simulation.calculate("taxable_income_deductions", year), federal_deductions
        )
        np.testing.assert_array_equal(
            simulation.calculate("mt_state_income_tax_itemized_add_back", year),
            adjustment,
        )
        actual = simulation.calculate("mt_taxable_income_joint", year)
        np.testing.assert_array_equal(actual, expected)
        assert np.all(actual <= old_floor_then_add)
        # Keep a binding floor and a nonbinding floor in every generated batch.
        assert actual[-2] == 0 < old_floor_then_add[-2]
        assert actual[-1] == old_floor_then_add[-1] == 35_400
