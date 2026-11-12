"""Compare Montana's chosen medical split with an independent share grid.

Form 2 permits spouses to divide jointly paid dependent bills in any proportion.
For each generated couple, the chosen combined line 20 cannot exceed any grid
share, including when one or both capital gain credits exhaust a column's tax.
Swapping columns and adding dependent bills cannot raise the combined tax.
The oracle uses the Form 2 schedules and the model's dependent-exemption
allocation convention, without calling the closed-form tax helpers.
"""

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation


# Form 2 instructions: 2021 p. 15, 2022 p. 16, 2023 p. 18.
THRESHOLDS = {
    2021: [0, 3_100, 5_500, 8_400, 11_400, 14_600, 18_800],
    2022: [0, 3_300, 5_800, 8_900, 12_000, 15_400, 19_800],
    2023: [0, 3_600, 6_300, 9_700, 13_000, 16_800, 21_600],
}
EXEMPTION = {2021: 2_580, 2022: 2_710, 2023: 2_960}


@st.composite
def couples(draw):
    agi = draw(st.lists(st.integers(0, 80_000), min_size=2, max_size=2))
    return {
        "agi": agi,
        "gains": [draw(st.integers(0, amount)) for amount in agi],
        "own": draw(st.lists(st.integers(0, 12_000), min_size=2, max_size=2)),
        "other": draw(st.lists(st.integers(0, 8_000), min_size=2, max_size=2)),
        "premiums": draw(st.lists(st.integers(0, 6_000), min_size=2, max_size=2)),
        "children": draw(st.integers(1, 3)),
        "bills": draw(st.integers(1, 50_000)),
    }


def _situation(cases, year):
    people, units, households = {}, {}, {}
    for i, case in enumerate(cases):
        members = []
        for j in range(2):
            name = f"u{i}_filer{j}"
            members.append(name)
            people[name] = {
                "age": {year: 40},
                "is_tax_unit_head": {year: j == 0},
                "is_tax_unit_spouse": {year: j == 1},
                "mt_agi_indiv": {year: case["agi"][j]},
                "long_term_capital_gains": {year: case["gains"][j]},
                "other_medical_expenses": {year: case["own"][j]},
                "mt_non_medical_itemized_deductions_indiv": {year: case["other"][j]},
                "mt_eligible_medical_insurance_premiums": {year: case["premiums"][j]},
            }
        for j in range(case["children"]):
            name = f"u{i}_child{j}"
            members.append(name)
            people[name] = {
                "age": {year: 10},
                "is_tax_unit_dependent": {year: True},
                "other_medical_expenses": {year: case["bills"] if j == 0 else 0},
            }
        units[f"u{i}"] = {"members": members, "mt_tax_unit_itemizes": {year: True}}
        households[f"u{i}"] = {"members": members, "state_code": {year: "MT"}}
    return {"people": people, "tax_units": units, "households": households}


def _grid_tax(case, year, shares):
    shares = np.array([shares, 1 - shares]).T
    deduction = (
        np.maximum(
            np.array(case["own"])
            + shares * case["bills"]
            - 0.075 * np.array(case["agi"]),
            0,
        )
        + case["other"]
        + np.array(case["premiums"])
    )
    pre = np.maximum(np.array(case["agi"]) - EXEMPTION[year] - deduction, 0)
    dependent = EXEMPTION[year] * case["children"]
    balanced = np.maximum((pre.sum(axis=1) - dependent) / 2, 0)
    taxable = np.minimum(pre, np.maximum(pre - dependent, balanced[:, None]))
    rates = np.array(
        [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.069 if year == 2021 else 0.0675]
    )
    tax = (
        np.maximum(taxable[:, :, None] - THRESHOLDS[year], 0)
        * np.diff(rates, prepend=0)
    ).sum(axis=2)
    return np.maximum(tax - 0.02 * np.array(case["gains"]), 0).sum(axis=1)


def _check(cases, year):
    variants = []
    for case in cases:
        swapped = {
            key: value[::-1] if isinstance(value, list) else value
            for key, value in case.items()
        }
        variants.extend([case, swapped, {**case, "bills": case["bills"] + 1_000}])
    sim = Simulation(situation=_situation(variants, year))
    assert sim.calculate("tax_unit_married", year).all()
    share = sim.calculate("mt_dependent_medical_expense_head_share", year)
    assert np.all((share >= 0) & (share <= 1))
    columns = sim.calculate("mt_income_tax_before_refundable_credits_indiv", year)
    tax = np.bincount(sim.populations["tax_unit"].members_entity_id, weights=columns)
    for i, case in enumerate(cases):
        # One cent covers the tie convention; the rest covers float32 income
        # and medical-share arithmetic at the generated income limits.
        tolerance = 0.03
        at_chosen_share = _grid_tax(case, year, np.array([share[3 * i]]))[0]
        assert abs(tax[3 * i] - at_chosen_share) <= tolerance
        expected = _grid_tax(case, year, np.linspace(0, 1, 1_001)).min()
        assert tax[3 * i] <= expected + tolerance
        assert abs(tax[3 * i] - tax[3 * i + 1]) <= tolerance
        assert tax[3 * i + 2] <= tax[3 * i] + tolerance


@settings(max_examples=6, deadline=None, derandomize=True)
@given(st.sampled_from(list(THRESHOLDS)), st.lists(couples(), min_size=4, max_size=12))
def test_credit_aware_medical_split(year, cases):
    _check(cases, year)


@pytest.mark.parametrize("year", THRESHOLDS)
def test_credit_exhaustion_witness(year):
    _check(
        [
            {
                "agi": [20_000, 20_000],
                "gains": [10_000, 0],
                "own": [0, 0],
                "other": [0, 0],
                "premiums": [0, 0],
                "children": 1,
                "bills": 25_000,
            },
            {
                "agi": [100_000, 100_000],
                "gains": [100_000, 0],
                "own": [0, 0],
                "other": [0, 0],
                "premiums": [0, 0],
                "children": 1,
                "bills": 150_000,
            },
        ],
        year,
    )
