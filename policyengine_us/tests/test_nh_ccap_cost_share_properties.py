"""Invariants of New Hampshire's child care family cost share, He-C 6910.18.

1. Step 1: a family at or below 100% of the poverty guidelines owes nothing.
2. Step 2: a family above 100% and at or below 138% owes $5 a week.
3. Step 3: a family above 138% owes 7% of monthly income divided by 4.33 weeks,
   and within the step the share rises with income.
4. For a family with one eligible child and no disability supplement, the
   monthly payment equals 52/12 weeks of the lesser of the charge and the standard
   rate, less the cost share, floored at zero.

rule_cost_share restates the rule's table on its own, so the variable and the
table must agree. The YAML cases pin single families; these draw incomes and
charges across the steps.
"""

from hypothesis import assume, example, given, settings
from hypothesis import strategies as st
import pytest

from policyengine_us import Simulation

YEAR = 2025
# He-C 6910.18(e) applies each year's poverty guidelines from the following July,
# so July 2025 uses the 2025 guideline for a family of two.
MONTH = "2025-07"
FPG = 21_150
WEEKLY_RATE = 280  # Preschool, full time, licensed center.
TOLERANCE = 0.01


def rule_cost_share(annual_income):
    if annual_income <= FPG:
        return 0
    if annual_income * 100 <= FPG * 138:
        return 5
    return annual_income / 12 * 0.07 / 4.33


def outside_boundary_slivers(annual_income):
    # The parameters place the steps at 1.0001 and 1.3801 of the guideline, so a
    # family inside those slivers takes the lower step.
    # Integer cross-products keep 138% of the guideline, $29,187, out of the sliver.
    in_first = FPG * 10_000 < annual_income * 10_000 < FPG * 10_001
    in_second = FPG * 13_800 < annual_income * 10_000 < FPG * 13_801
    return not (in_first or in_second)


def cost_share_and_payment(annual_income, annual_charge):
    members = ["parent", "child"]
    parent = {
        "age": {YEAR: 28},
        "weekly_hours_worked_before_lsr": {YEAR: 40},
        "employment_income": {YEAR: annual_income},
    }
    child = {
        "age": {YEAR: 4},
        "is_tax_unit_dependent": {YEAR: True},
        "immigration_status": {YEAR: "CITIZEN"},
        "childcare_hours_per_week": {YEAR: 40},
        "nh_ccap_provider_type": {YEAR: "LICENSED_CENTER"},
        "pre_subsidy_childcare_expenses": {YEAR: annual_charge},
    }
    situation = {
        "people": {"parent": parent, "child": child},
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {YEAR: "NH"}}},
    }
    simulation = Simulation(situation=situation)
    return [
        float(simulation.calculate(name, MONTH)[0])
        for name in ("nh_ccap_cost_share", "nh_ccap")
    ]


@settings(max_examples=15, deadline=None)
# Zero income, each step's upper edge, the first dollars above 138%, and a charge
# below the rate that the cost share exceeds.
@example(annual_income=0, annual_charge=18_720)
@example(annual_income=FPG, annual_charge=18_720)
@example(annual_income=FPG * 138 // 100, annual_charge=18_720)
@example(annual_income=29_200, annual_charge=18_720)
@example(annual_income=48_000, annual_charge=18_720)
@example(annual_income=80_000, annual_charge=1_000)
@given(
    annual_income=st.integers(min_value=0, max_value=80_000),
    annual_charge=st.integers(min_value=1, max_value=40_000),
)
def test_cost_share_and_payment_follow_the_rule(annual_income, annual_charge):
    assume(outside_boundary_slivers(annual_income))
    share, payment = cost_share_and_payment(annual_income, annual_charge)
    expected_share = rule_cost_share(annual_income)
    assert share == pytest.approx(expected_share, abs=TOLERANCE)
    weekly_cap = min(annual_charge / 52, WEEKLY_RATE)
    expected_payment = max(weekly_cap - expected_share, 0) * 52 / 12
    assert payment == pytest.approx(expected_payment, abs=TOLERANCE)


@settings(max_examples=10, deadline=None)
@given(
    lower=st.integers(min_value=29_190, max_value=79_999),
    gap=st.integers(min_value=1, max_value=20_000),
)
def test_step_three_share_rises_with_income(lower, gap):
    higher = min(lower + gap, 80_000)
    lower_share, _ = cost_share_and_payment(lower, 18_720)
    higher_share, _ = cost_share_and_payment(higher, 18_720)
    assert higher_share > lower_share
