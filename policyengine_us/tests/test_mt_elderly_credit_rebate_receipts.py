"""Actual cash receipts enter Montana household income once, without inference.

SB542 sections 1(3),3(5) require qualifying occupancy and a claim, so a prior
property-tax bill alone cannot establish a receipt. Statutory gross household
income includes all nontaxable income (HB191 section1(9), PDFp2), including
rebate cash in2023 despite omission from that year's illustrative form list.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from policyengine_us import Simulation


def build_situation(cases, year, with_receipts):
    people, tax_units, households = {}, {}, {}
    for i, c in enumerate(cases):
        # No receipt input is supplied anywhere in A/B's simulation. Core
        # defaults omitted person rows once any row supplies an input, so C
        # must be in another simulation to exercise absence of that input.
        for arrangement in "C" if with_receipts else "AB":
            key = f"{arrangement}{i}"
            members = [f"claimant{key}", f"member{key}"]
            for j, name in enumerate(members):
                people[name] = {
                    "age": {year: 70 if j == 0 else 40},
                    "taxable_pension_income": {year: c["pension"] if j == 0 else 0},
                    "is_tax_unit_dependent": {year: False},
                    "real_estate_taxes": {
                        year: c["property_tax"] if j == 0 else 0,
                        year - 1: c["prior_tax"]
                        if arrangement == "A" and j == 0
                        else 0,
                    },
                    "mt_refundable_credits_before_renter_credit": {year: 0},
                    "mt_elderly_homeowner_or_renter_credit_received": {year: 0},
                }
                if arrangement == "C":
                    people[name][
                        "mt_elderly_homeowner_or_renter_credit_property_tax_rebate_received"
                    ] = {year: c["receipts"][j]}
                tax_units[f"{name}_return"] = {
                    "members": [name],
                    "income_tax_refundable_credits": {year: 0},
                }
            households[f"household{key}"] = {
                "members": members,
                "state_code": {year: "MT", year - 1: "MT"},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def calculate(cases, year, with_receipts):
    sim = Simulation(situation=build_situation(cases, year, with_receipts))
    shape = (len(cases), 1 if with_receipts else 2)
    return {
        name: np.asarray(sim.calculate(variable, year, map_to="household")).reshape(
            shape
        )
        for name, variable in {
            "income": "mt_elderly_homeowner_or_renter_credit_gross_household_income",
            "credit": "mt_elderly_homeowner_or_renter_credit",
            "receipts": "mt_elderly_homeowner_or_renter_credit_property_tax_rebate_received",
        }.items()
    }


def assert_receipts(cases, year):
    absent = calculate(cases, year, with_receipts=False)
    supplied = calculate(cases, year, with_receipts=True)
    for i, c in enumerate(cases):
        cash = sum(c["receipts"])
        assert absent["receipts"][i] == pytest.approx([0, 0], abs=0.01)
        assert supplied["receipts"][i, 0] == pytest.approx(cash, abs=0.01)
        assert absent["income"][i] == pytest.approx([c["pension"]] * 2, abs=0.01)
        assert supplied["income"][i, 0] == pytest.approx(c["pension"] + cash, abs=0.01)
        assert absent["credit"][i, 0] == pytest.approx(absent["credit"][i, 1], abs=0.01)
        assert supplied["credit"][i, 0] <= absent["credit"][i, 0] + 0.01
    return absent["credit"], supplied["credit"]


def test_reviewer_unreceived_rebate():
    # No receipt: 1000-(20000-12600)*.035=741. The old assumed400 gave727.
    absent, supplied = assert_receipts(
        [
            {
                "pension": 20000,
                "property_tax": 1000,
                "prior_tax": 1000,
                "receipts": [400, 0],
            }
        ],
        2025,
    )
    assert absent[0] == pytest.approx([741, 741], abs=0.01)
    assert supplied[0, 0] == pytest.approx(727, abs=0.01)


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    cases=st.lists(
        st.fixed_dictionaries(
            {
                "pension": st.integers(0, 45000),
                "property_tax": st.integers(0, 4000),
                "prior_tax": st.integers(0, 4000),
                "receipts": st.lists(st.integers(0, 675), min_size=2, max_size=2),
            }
        ),
        min_size=1,
        max_size=4,
    ),
    year=st.sampled_from([2023, 2024, 2025]),
)
def test_actual_receipts_count_once_and_prior_tax_does_not_imply_receipt(cases, year):
    assert_receipts(cases, year)
