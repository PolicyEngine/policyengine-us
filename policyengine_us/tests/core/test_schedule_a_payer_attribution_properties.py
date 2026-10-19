"""Schedule A counts the premiums the filers paid, not a dependent's own.

IRC 213(a) allows medical expenses the taxpayer paid for the taxpayer, the
spouse and dependents. Premium inputs sit on the person who paid them, so a
parent-paid policy covering a dependent is the parent's input, and a
dependent's premium input is the dependent's own payment. Other medical
expenses sit on the person cared for, including amounts the parents paid on a
dependent's behalf, so every member's count.

Hypothesis draws batches of single and joint returns with one or two
dependents, premiums and other medical expenses on every member, and a
supplied self-employed health insurance deduction. For each return it builds
these variants in one vectorized simulation per year:

- the drawn return;
- the same return with part of one filer's premiums moved to a dependent;
- that return with the premiums moved back;
- the drawn return with the head and spouse labels exchanged;
- the drawn return with every dependent's premiums set to 0.

Invariants, for every drawn return:

1. Differential: `itemized_medical_expenses` equals an independent oracle,
   max(0, filer premiums - deduction) + every member's other medical
   expenses.
2. Dependent invariance: the filers' subtotal, federal medical deduction,
   New Mexico's medical care expense deduction (PIT-1 line 16) and senior
   medical credit and exemption, New Jersey's medical expense deduction and
   Montana's 2021-2023 joint medical deduction do not depend on a
   dependent's own premiums.
3. Payer move: moving premiums from a filer to a dependent never raises any of
   those amounts, and moving them back restores each to the cent.
4. Labels: exchanging the head and spouse labels changes none of them, nor
   North Dakota's renter refund income.
5. North Dakota: NDCC 57-02-08.1(5)(c) takes out medical expenses paid by the
   applicant or the applicant's dependent, so renter refund income does not
   change when premiums move between a filer and a dependent, and it equals
   income less every member's premiums and other medical expenses.

YAML covers the legal examples; these properties check the payer rule across
generated returns and every reader at once.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

CENT = 0.01
# Variables read on the filers' return, by the year in which they apply.
FILER_AMOUNTS = {
    # Montana's itemized schedule applies 2021-2023.
    2022: ["mt_medical_expense_deduction_joint"],
    # New Mexico's medical care expense deduction ends after 2024.
    2024: [
        "itemized_medical_expenses",
        "medical_expense_deduction",
        "nm_medical_care_expense_deduction",
        "nm_medical_expense_credit",
        "nm_medical_expense_exemption",
        "nj_medical_expense_deduction",
    ],
}
STATES = {2022: ["MT"], 2024: ["NM", "NJ"], 2025: ["ND"]}
VARIANTS = ["drawn", "moved", "moved_back", "swapped", "no_dependent_premiums"]


@st.composite
def returns(draw):
    joint = draw(st.booleans())
    dependents = draw(st.integers(1, 2))
    filers = 2 if joint else 1
    premiums = [draw(st.integers(0, 20_000)) for _ in range(filers + dependents)]
    other = [draw(st.integers(0, 15_000)) for _ in range(filers + dependents)]
    filer_premiums = sum(premiums[:filers])
    mover = draw(st.integers(0, filers - 1))
    return {
        "joint": joint,
        "filers": filers,
        "premiums": premiums,
        "other": other,
        "head_age": draw(st.sampled_from([45, 66])),
        "income": draw(st.integers(0, 120_000)),
        # Within the filers' premiums, as the payer contract requires, or
        # above them.
        "deduction": draw(st.integers(0, filer_premiums + 5_000)),
        "mover": mover,
        "moved": draw(st.integers(0, premiums[mover])),
        "receiver": filers + draw(st.integers(0, dependents - 1)),
    }


def _variant(case, variant):
    premiums = list(case["premiums"])
    head, spouse = 0, 1 if case["joint"] else None
    if variant == "moved":
        premiums[case["mover"]] -= case["moved"]
        premiums[case["receiver"]] += case["moved"]
    elif variant == "no_dependent_premiums":
        premiums[case["filers"] :] = [0] * (len(premiums) - case["filers"])
    elif variant == "swapped" and case["joint"]:
        head, spouse = 1, 0
    # "moved_back" undoes "moved": its inputs are the drawn ones.
    return premiums, head, spouse


def _simulation(cases, year):
    people, tax_units, households, marital_units = {}, {}, {}, {}
    rows = []
    for state in STATES[year]:
        for case_index, case in enumerate(cases):
            for variant in VARIANTS:
                unit = f"{state}_{case_index}_{variant}"
                premiums, head, spouse = _variant(case, variant)
                names = []
                for index, paid in enumerate(premiums):
                    name = f"{unit}_{index}"
                    names.append(name)
                    filer = index < case["filers"]
                    people[name] = {
                        variable: {year: value}
                        for variable, value in {
                            "age": (case["head_age"] if index == 0 else 40)
                            if filer
                            else 17,
                            "is_tax_unit_head": index == head,
                            "is_tax_unit_spouse": index == spouse,
                            "is_tax_unit_dependent": not filer,
                            "employment_income": case["income"] if index == 0 else 0,
                            "medicare_enrolled": False,
                            "health_insurance_premiums": paid,
                            "other_medical_expenses": case["other"][index],
                        }.items()
                    }
                    if not filer:
                        marital_units[f"{name}_marital_unit"] = {"members": [name]}
                marital_units[f"{unit}_marital_unit"] = {
                    "members": names[: case["filers"]]
                }
                tax_units[unit] = {
                    "members": names,
                    "self_employed_health_insurance_ald": {year: case["deduction"]},
                }
                households[unit] = {"members": names, "state_code": {year: state}}
                rows.append((state, case_index, variant))
    simulation = Simulation(
        tax_benefit_system=system,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            "marital_units": marital_units,
        },
    )
    return simulation, rows


def _by_row(values, rows):
    return {row: value for row, value in zip(rows, values)}


def _tax_unit_amount(simulation, variable, year):
    entity = simulation.tax_benefit_system.variables[variable].entity.key
    values = simulation.calculate(variable, year)
    if entity == "person":
        # Montana reports the joint deduction on the head; sum over the unit.
        return simulation.map_result(values, "person", "tax_unit")
    return values


def _assert_filer_amounts(cases, year):
    simulation, rows = _simulation(cases, year)
    for variable in FILER_AMOUNTS[year]:
        values = _by_row(_tax_unit_amount(simulation, variable, year), rows)
        for state in STATES[year]:
            for case_index, case in enumerate(cases):
                key = (state, case_index)
                drawn = values[(*key, "drawn")]
                # 2. A dependent's own premiums do not reach the filers.
                np.testing.assert_allclose(
                    values[(*key, "no_dependent_premiums")], drawn, atol=CENT
                )
                # 3. Moving premiums to a dependent never raises the amount,
                # and moving them back restores it.
                assert values[(*key, "moved")] <= drawn + CENT, (variable, case)
                np.testing.assert_allclose(
                    values[(*key, "moved_back")], drawn, atol=CENT
                )
                # 4. Either spouse may be labelled head.
                np.testing.assert_allclose(values[(*key, "swapped")], drawn, atol=CENT)
    return simulation, rows


@settings(max_examples=8, deadline=None, derandomize=True)
@given(cases=st.lists(returns(), min_size=2, max_size=3))
def test_filers_count_only_their_own_premium_payments(cases):
    simulation, rows = _assert_filer_amounts(cases, 2024)
    # 1. Differential against an independent oracle.
    subtotal = _by_row(simulation.calculate("itemized_medical_expenses", 2024), rows)
    for (state, case_index, variant), value in subtotal.items():
        case = cases[case_index]
        premiums, _, _ = _variant(case, variant)
        filer_premiums = sum(premiums[: case["filers"]])
        expected = max(0, filer_premiums - case["deduction"]) + sum(case["other"])
        assert value == pytest.approx(expected, abs=CENT), (variant, case)
    _assert_filer_amounts(cases, 2022)


@settings(max_examples=8, deadline=None, derandomize=True)
@given(cases=st.lists(returns(), min_size=2, max_size=3))
def test_north_dakota_counts_premiums_either_payer_made(cases):
    simulation, rows = _simulation(cases, 2025)
    income = _by_row(simulation.calculate("nd_renters_refund_income", 2025), rows)
    for case_index, case in enumerate(cases):
        drawn = income[("ND", case_index, "drawn")]
        # 5. Every member's premiums and other medical expenses come off.
        expected = max(0, case["income"] - sum(case["premiums"]) - sum(case["other"]))
        assert drawn == pytest.approx(expected, abs=CENT), case
        for variant in ("moved", "moved_back", "swapped"):
            np.testing.assert_allclose(
                income[("ND", case_index, variant)], drawn, atol=CENT
            )
