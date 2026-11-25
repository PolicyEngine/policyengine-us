"""Resident-specific elections in a mixed federal-itemizer population."""

import numpy as np
from policyengine_core.reforms import Reform

from policyengine_us import Simulation


def test_new_york_tuition_and_virginia_sales_elections_share_a_population():
    year = 2025
    # Each column represents a separate resident return.
    situation = {
        "state_code": {year: ["NY", "NY", "VA"]},
        "in_nyc": {year: [False, True, False]},
        "age": {year: [40, 40, 40]},
        "employment_income": {year: [60_000, 60_000, 150_000]},
        "deductible_mortgage_interest": {year: [16_000, 16_000, 20_000]},
        "qualified_tuition_expenses": {year: [3_000, 3_000, 0]},
        "tax_unit_itemizes": {year: [True, True, True]},
        "state_withheld_income_tax": {year: [8_000, 8_000, 8_000]},
        "state_sales_tax": {year: [0, 0, 7_800]},
        "local_sales_tax": {year: [0, 0, 0]},
    }
    bills = ("income_tax", "state_income_tax", "local_tax")

    # Price the filed alternatives on fresh simulations with the optimizer off.
    def filed_bills(tuition_credit, sales_tax):
        filed = Simulation(situation=situation)
        filed.set_input("state_deduction_method", year, ["ITEMIZED"] * 3)
        filed.set_input("ny_elects_tuition_credit_when_itemizing", year, tuition_credit)
        filed.set_input("state_and_local_sales_tax_elected", year, sales_tax)
        return np.array([filed.calculate(name, year) for name in bills])

    # Only the upstate filer elects the tuition credit. NYC resident tax makes
    # the tuition deduction preferable in the city. Virginia keeps sales tax
    # on its Schedule A and subtracts income tax on the competing return.
    tuition = [True, False, False]
    sales = [False, False, True]
    expected = filed_bills(tuition, sales)
    competing = filed_bills([False, True, False], [False, False, False])
    assert (expected.sum(axis=0) < competing.sum(axis=0)).all()
    assert expected[2, 1] > 0

    joint = Simulation(situation=situation)
    joint.apply_reform(
        Reform.from_dict(
            {"gov.simulation.joint_federal_state_itemization": {"2025": True}}
        )
    )
    np.testing.assert_array_equal(
        joint.calculate("ny_elects_tuition_credit_when_itemizing", year), tuition
    )
    np.testing.assert_array_equal(
        joint.calculate("state_and_local_sales_tax_elected", year), sales
    )
    np.testing.assert_array_equal(
        joint.calculate("state_deduction_method", year).decode_to_str(),
        ["ITEMIZED"] * 3,
    )
    for name, expected_bill in zip(bills, expected, strict=True):
        np.testing.assert_allclose(
            joint.calculate(name, year), expected_bill, rtol=0, atol=0.01
        )
