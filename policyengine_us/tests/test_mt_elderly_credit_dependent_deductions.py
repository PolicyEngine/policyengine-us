"""Own valid adjustments reduce Montana household income once, losses never do.

2023 Form 2 instructions p.51 line 1 uses each household member's federal
AGI. HB191 section 1(9), PDF p.2, retains federal AGI without regard to loss.
These properties compare a dependent with a member on a separate return,
holding receipts fixed at zero to isolate their non-loss deductions.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from policyengine_us import Simulation


def build_situation(cases, year):
    people, tax_units, marital_units, spm_units, families, households = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for index, case in enumerate(cases):
        # A: dependent; B: separate filer; C: no losses; D: extra own penalty.
        for arrangement in "ABCD":
            key = f"{arrangement}{index}"
            claimant, member = f"claimant_{key}", f"member_{key}"
            people[claimant] = {
                "age": {year: 70},
                "taxable_pension_income": {year: case["pension"]},
                "early_withdrawal_penalty": {year: case["parent_penalty"]},
                "is_tax_unit_dependent": {year: False},
                "mt_refundable_credits_before_renter_credit": {year: 0},
                "mt_elderly_homeowner_or_renter_credit_received": {year: 0},
                "mt_elderly_homeowner_or_renter_credit_property_tax_rebate_received": {
                    year: 0
                },
            }
            people[member] = {
                "age": {year: 19},
                "is_tax_unit_dependent": {year: arrangement != "B"},
                "employment_income": {year: case["wages"]},
                "self_employment_income": {year: case["self_employment"]},
                "taxable_interest_income": {year: case["interest"]},
                "traditional_ira_contributions": {year: case["ira"]},
                "educator_expense": {year: case["educator"]},
                "early_withdrawal_penalty": {
                    year: case["penalty"]
                    + (case["extra_penalty"] if arrangement == "D" else 0)
                },
                "self_employed_health_insurance_premiums": {year: case["health"]},
                "self_employed_pension_contributions": {
                    year: case["pension_contribution"]
                },
                "long_term_capital_gains": {
                    year: -case["capital_loss"] if arrangement != "C" else 0
                },
                "rental_income": {
                    year: -case["rental_loss"] if arrangement != "C" else 0
                },
                "mt_refundable_credits_before_renter_credit": {year: 0},
                "mt_elderly_homeowner_or_renter_credit_received": {year: 0},
                "mt_elderly_homeowner_or_renter_credit_property_tax_rebate_received": {
                    year: 0
                },
            }
            tax_units[f"tax_unit_{key}"] = {
                "members": [claimant] if arrangement == "B" else [claimant, member],
                "health_savings_account_ald": {year: case["parent_hsa"]},
                "income_tax_refundable_credits": {year: 0},
            }
            if arrangement == "B":
                tax_units[f"member_tax_unit_{key}"] = {
                    "members": [member],
                    "health_savings_account_ald": {year: 0},
                    "income_tax_refundable_credits": {year: 0},
                }
            marital_units[f"claimant_marital_unit_{key}"] = {"members": [claimant]}
            marital_units[f"member_marital_unit_{key}"] = {"members": [member]}
            spm_units[f"spm_unit_{key}"] = {"members": [claimant, member]}
            families[f"family_{key}"] = {"members": [claimant, member]}
            households[f"household_{key}"] = {
                "members": [claimant, member],
                "state_code": {year: "MT"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": households,
    }


def assert_properties(cases, year):
    simulation = Simulation(situation=build_situation(cases, year))
    income = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income", year
        )
    ).reshape(len(cases), 4, 2)
    for index, case in enumerate(cases):
        # Schedule SE p.1: net earnings x .9235 x (.124 + .029) / 2.
        # Generated positive profits exceed the $400 net-earnings threshold
        # and remain below the Social Security wage base.
        self_employment_deduction = case["self_employment"] * 0.9235 * 0.153 / 2
        # Pub.590-A (2023) p.11: the deduction cannot exceed contributions,
        # compensation, or the annual limit ($6,500 in 2023; $7,000 in
        # 2024–25). These single members' MAGI is below the phase-out start.
        # Compensation excludes the half-SE-tax and SE retirement deduction.
        compensation = case["wages"] + max(
            0,
            case["self_employment"]
            - self_employment_deduction
            - case["pension_contribution"],
        )
        ira_deduction = min(case["ira"], compensation, 6_500 if year == 2023 else 7_000)
        # 2023 Form1040 instructions p.89: the per-educator cap is $300;
        # the cap remains $300 in the other generated years.
        educator_deduction = min(case["educator"], 300)
        own_deductions = (
            self_employment_deduction
            + case["health"]
            + case["pension_contribution"]
            + ira_deduction
            + educator_deduction
            + case["penalty"]
        )
        parent = case["pension"] - case["parent_hsa"] - case["parent_penalty"]
        member = (
            case["wages"] + case["self_employment"] + case["interest"] - own_deductions
        )
        tol = max(0.01, 8 * float(np.spacing(np.float32(abs(parent + member)))))
        # Each person's non-loss deductions are used once, on that person.
        assert income[index, :, 0] == pytest.approx([parent] * 4, abs=tol)
        assert income[index, :3, 1] == pytest.approx([member] * 3, abs=tol)
        # The filing arrangement leaves total household income unchanged.
        assert income[index, 0].sum() == pytest.approx(income[index, 1].sum(), abs=tol)
        # Removing capital/rental losses never changes this statutory total.
        assert income[index, 0].sum() == pytest.approx(income[index, 2].sum(), abs=tol)
        # Another dollar of the dependent's valid penalty is deducted once.
        assert income[index, 3, 1] == pytest.approx(
            member - case["extra_penalty"], abs=tol
        )


def test_worked_deductions_and_losses():
    case = {
        "pension": 20_000,
        "parent_hsa": 1_000,
        "parent_penalty": 50,
        "wages": 10_000,
        "self_employment": 15_000,
        "interest": 500,
        "ira": 1_000,
        "educator": 100,
        "penalty": 200,
        "health": 500,
        "pension_contribution": 600,
        "capital_loss": 3_000,
        "rental_loss": 2_000,
        "extra_penalty": 300,
    }
    # Parent = 20,000 - 1,000 - 50 = 18,950. Member = 25,500 - 1,059.71625
    # - 1,000 - 100 - 200 - 500 - 600 = 22,040.28375; extra penalty ->
    # 21,740.28375. Neither of the two losses affects these amounts.
    assert_properties([case], 2023)


@st.composite
def case_strategy(draw):
    # Keep health/pension limits nonbinding, including after half-SE-tax:
    # at the minimum $5,000 profit, half-SE-tax = $353.23875. With pension
    # $500, Form7206 lines7-10,14 allow health up to $4,146.76125; the
    # SEP 20% ceiling is ($5,000 - $353.23875) * .2 = $929.35225.
    # https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1
    # https://www.irs.gov/pub/irs-prior/p560--2023.pdf#page=35 (PDFpp35-36)
    return {
        "pension": draw(st.integers(10_000, 35_000)),
        "parent_hsa": draw(st.integers(0, 3_000)),
        "parent_penalty": draw(st.integers(0, 500)),
        "wages": draw(st.integers(10_000, 20_000)),
        "self_employment": draw(st.integers(5_000, 15_000)),
        "interest": draw(st.integers(0, 10_000)),
        "ira": draw(st.integers(0, 10_000)),
        "educator": draw(st.integers(0, 1_000)),
        "penalty": draw(st.integers(0, 1_000)),
        "health": draw(st.integers(0, 500)),
        "pension_contribution": draw(st.integers(0, 500)),
        "capital_loss": draw(st.integers(0, 20_000)),
        "rental_loss": draw(st.integers(0, 20_000)),
        "extra_penalty": draw(st.integers(1, 2_000)),
    }


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    cases=st.lists(case_strategy(), min_size=1, max_size=4),
    year=st.sampled_from([2023, 2024, 2025]),
)
def test_own_deductions_and_losses_are_independent_of_filing_arrangement(cases, year):
    assert_properties(cases, year)
