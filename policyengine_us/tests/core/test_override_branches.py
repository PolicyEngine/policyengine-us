"""Formula branches calculate under their overrides, whatever was cached first.

Several formulas compare a tax unit's liability under alternative choices by
calculating it in a branch with one input overridden: itemizing or not
(``tax_unit_itemizes``), Delaware and Virginia EITC refundability, the Idaho
aged or disabled credit or deduction, Missouri TANF caretaker inclusion and
Medicaid for SSI state supplements. A policyengine-core branch starts as a copy
of every array its parent has cached, and setting an input on it clears none
of them, so a value the parent calculated from the old input answers for the
branch. ``get_override_branch`` drops the copied values when the parent has
already calculated the overridden input, and creates the branch again for each
period.

The non-refundable CTC used to be limited by the tax liability recomputed
without the SALT deduction, in a "no_salt" branch. The branch usually inherited
the liability with SALT, so the CTC depended on which variables a caller asked
for first. 26 U.S.C. 26(a) limits the credit by the actual tax liability, SALT
deduction included, and ``ctc_limiting_tax_liability`` now reads it directly.

A seeded sample of households shares one simulation; the tests check:

1. The CTC-limiting liability is income tax before credits less the other
   non-refundable credits, and the non-refundable and refundable parts add up
   to the credit.
2. Every reported variable is the same whichever variable is calculated first.
3. Each comparison branch equals a fresh simulation that sets the overridden
   input before anything is calculated (a differential test of the branch
   against the reference path).
4. The same holds when the parent has already calculated the overridden
   input, and when an earlier year was calculated first.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.tools.override_branch import (
    drop_inherited_values,
    get_override_branch,
)

YEAR = 2026
SEED = 20261001
N = 48
STATES = ["CA", "NY", "VA", "DE", "ID", "NJ", "MA", "IL", "TX", "OR"]
REPORTED = [
    "income_tax",
    "income_tax_before_credits",
    "ctc_limiting_tax_liability",
    "non_refundable_ctc",
    "refundable_ctc",
    "tax_unit_itemizes",
    "state_income_tax",
    "household_net_income",
]


def _sample():
    rng = np.random.default_rng(SEED)
    households = []
    for i in range(N):
        married = bool(rng.random() < 0.6)
        children = int(rng.integers(0, 4))
        earnings = float(np.round(np.exp(rng.uniform(np.log(8_000), np.log(300_000)))))
        households.append(
            dict(
                state=STATES[i % len(STATES)],
                married=married,
                children=children,
                earnings=earnings,
                spouse_share=float(rng.choice([0, 0.2, 0.5])) if married else 0,
                mortgage=float(rng.choice([0, 8_000, 18_000, 30_000])),
                property_tax=float(rng.choice([0, 3_000, 9_000, 16_000])),
                charity=float(rng.choice([0, 2_000, 9_000])),
                aged_parent=bool(rng.random() < 0.15),
            )
        )
    return households


def _situation(households, years=(YEAR,), itemizes=None):
    people, units, marital = {}, {}, {}
    for i, h in enumerate(households):
        members = []

        def add(name, **inputs):
            people[name] = {k: {y: v for y in years} for k, v in inputs.items()}
            members.append(name)

        head = f"h{i}"
        earnings = h["earnings"]
        add(
            head,
            age=40,
            employment_income=earnings * (1 - h["spouse_share"]),
            deductible_mortgage_interest=h["mortgage"],
            real_estate_taxes=h["property_tax"],
            charitable_cash_donations=h["charity"],
        )
        marital[f"mu_{head}"] = {"members": [head]}
        if h["married"]:
            add(f"s{i}", age=38, employment_income=earnings * h["spouse_share"])
            marital[f"mu_{head}"]["members"].append(f"s{i}")
        for c in range(h["children"]):
            add(f"c{i}_{c}", age=3 + 4 * c, is_tax_unit_dependent=True)
            marital[f"mu_c{i}_{c}"] = {"members": [f"c{i}_{c}"]}
        if h["aged_parent"]:
            add(
                f"p{i}",
                age=74,
                is_tax_unit_dependent=True,
                share_of_care_and_support_costs_paid_by_tax_filer=1.0,
            )
            marital[f"mu_p{i}"] = {"members": [f"p{i}"]}
        units[i] = members
    tax_units = {f"tu{i}": {"members": m} for i, m in units.items()}
    if itemizes is not None:
        for i, unit in enumerate(tax_units.values()):
            unit["tax_unit_itemizes"] = {y: bool(itemizes[i]) for y in years}
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": {f"spm{i}": {"members": m} for i, m in units.items()},
        "families": {f"fam{i}": {"members": m} for i, m in units.items()},
        "marital_units": marital,
        "households": {
            f"hh{i}": {
                "members": m,
                "state_code": {y: households[i]["state"] for y in years},
            }
            for i, m in units.items()
        },
    }


@pytest.fixture(scope="module")
def households():
    return _sample()


@pytest.fixture(scope="module")
def baseline(households):
    simulation = Simulation(situation=_situation(households))
    return {v: simulation.calculate(v, YEAR) for v in REPORTED}


def test_ctc_limit_is_actual_liability_less_other_credits(households):
    simulation = Simulation(situation=_situation(households))
    limit = simulation.calculate("ctc_limiting_tax_liability", YEAR)
    before_credits = simulation.calculate("income_tax_before_credits", YEAR)
    credits = simulation.tax_benefit_system.parameters(YEAR).gov.irs.credits
    other = sum(
        simulation.calculate(credit, YEAR)
        for credit in credits.non_refundable
        if credit != "non_refundable_ctc"
    )
    np.testing.assert_allclose(limit, np.maximum(0, before_credits - other))
    ctc = simulation.calculate("ctc", YEAR)
    non_refundable = simulation.calculate("non_refundable_ctc", YEAR)
    refundable = simulation.calculate("refundable_ctc", YEAR)
    # non_refundable_ctc is the credit less its refundable part; the tax
    # limit applies when non-refundable credits are capped.
    assert (refundable <= ctc + 0.01).all()
    np.testing.assert_allclose(non_refundable + refundable, ctc, atol=0.01)
    # The sample includes itemizers with SALT whose CTC the limit binds.
    salt = simulation.calculate("salt_deduction", YEAR)
    itemizes = simulation.calculate("tax_unit_itemizes", YEAR)
    assert (itemizes & (salt > 0) & (limit < ctc)).any()


@pytest.mark.parametrize(
    "first",
    [
        "income_tax",
        "refundable_ctc",
        "ctc_value",
        "state_income_tax",
        "tax_liability_if_itemizing",
        "spm_unit_net_income",
    ],
)
def test_results_do_not_depend_on_calculation_order(households, baseline, first):
    simulation = Simulation(situation=_situation(households))
    simulation.calculate(first, YEAR)
    for variable in REPORTED:
        np.testing.assert_array_equal(
            simulation.calculate(variable, YEAR),
            baseline[variable],
            err_msg=f"{variable} changes when {first} is calculated first",
        )


def _fresh(households, variable, overrides, year=YEAR):
    simulation = Simulation(situation=_situation(households, years=(year,)))
    for name, value in overrides.items():
        simulation.set_input(name, year, value)
    return simulation.calculate(variable, year)


def test_itemization_branches_match_fresh_simulations(households):
    simulation = Simulation(situation=_situation(households))
    simulation.calculate("household_net_income", YEAR)
    n = len(households)
    for comparison, itemizes in (
        ("tax_liability_if_itemizing", True),
        ("tax_liability_if_not_itemizing", False),
    ):
        np.testing.assert_allclose(
            simulation.calculate(comparison, YEAR),
            _fresh(households, "income_tax", {"tax_unit_itemizes": [itemizes] * n}),
            atol=0.01,
            err_msg=comparison,
        )


@pytest.mark.parametrize(
    "comparison,variable,override,value",
    [
        (
            "de_income_tax_if_claiming_refundable_eitc",
            "de_income_tax",
            "de_claims_refundable_eitc",
            True,
        ),
        (
            "de_income_tax_if_claiming_non_refundable_eitc",
            "de_income_tax",
            "de_claims_refundable_eitc",
            False,
        ),
        (
            "va_income_tax_if_claiming_refundable_eitc",
            "va_income_tax",
            "va_claims_refundable_eitc",
            True,
        ),
        (
            "va_income_tax_if_claiming_non_refundable_eitc",
            "va_income_tax",
            "va_claims_refundable_eitc",
            False,
        ),
        (
            "id_income_tax_if_receiving_aged_or_disabled_credit",
            "id_income_tax",
            "id_receives_aged_or_disabled_credit",
            True,
        ),
        (
            "id_income_tax_if_receiving_aged_or_disabled_deduction",
            "id_income_tax",
            "id_receives_aged_or_disabled_credit",
            False,
        ),
    ],
)
def test_state_choice_branches_match_fresh_simulations(
    households, comparison, variable, override, value
):
    simulation = Simulation(situation=_situation(households))
    simulation.calculate("household_net_income", YEAR)
    np.testing.assert_allclose(
        simulation.calculate(comparison, YEAR),
        _fresh(households, variable, {override: [value] * len(households)}),
        atol=0.01,
    )


def test_branch_after_parent_calculated_the_overridden_input(households):
    # tax_unit_itemizes is an input here, so the parent calculates income tax
    # without the itemizing branch; the branch is created afterwards and must
    # not answer with the parent's income tax.
    n = len(households)
    situation = _situation(households, itemizes=[False] * n)
    simulation = Simulation(situation=situation)
    not_itemizing = simulation.calculate("income_tax", YEAR)
    itemizing = simulation.calculate("tax_liability_if_itemizing", YEAR)
    expected = _fresh(households, "income_tax", {"tax_unit_itemizes": [True] * n})
    np.testing.assert_allclose(itemizing, expected, atol=0.01)
    assert not np.allclose(itemizing, not_itemizing)


def test_later_year_branches_match_single_year_simulation(households):
    years = (2025, YEAR)
    simulation = Simulation(situation=_situation(households, years=years))
    simulation.calculate("tax_liability_if_itemizing", 2025)
    simulation.calculate("income_tax", 2025)
    fresh = Simulation(situation=_situation(households, years=years))
    for variable in REPORTED + ["tax_liability_if_itemizing"]:
        np.testing.assert_array_equal(
            simulation.calculate(variable, YEAR),
            fresh.calculate(variable, YEAR),
            err_msg=f"{variable} for {YEAR} depends on 2025 being calculated first",
        )
    assert simulation.branches["itemizing"].branch_period.start.year == YEAR


def test_get_override_branch_reuses_within_period_and_recreates_otherwise(
    households,
):
    simulation = Simulation(situation=_situation(households, years=(2025, YEAR)))
    n = len(households)
    ones = np.ones(n, dtype=bool)
    first = get_override_branch(
        simulation, "test_branch", YEAR, {"tax_unit_itemizes": ones}
    )
    assert (
        get_override_branch(
            simulation, "test_branch", YEAR, {"tax_unit_itemizes": ones}
        )
        is first
    )
    other_inputs = get_override_branch(
        simulation, "test_branch", YEAR, {"tax_unit_itemizes": ~ones}
    )
    assert other_inputs is not first
    other_period = get_override_branch(
        simulation, "test_branch", 2025, {"tax_unit_itemizes": ones}
    )
    assert other_period is not other_inputs
    assert simulation.branches["test_branch"] is other_period


def test_drop_inherited_values_keeps_inputs_only(households):
    n = len(households)
    itemizes = np.ones(n, dtype=bool)
    simulation = Simulation(situation=_situation(households))
    simulation.calculate("income_tax", YEAR)
    # A plain branch with an input of its own, and a branch nested in it.
    parent = simulation.get_branch("parent_with_input")
    parent.set_input("tax_unit_itemizes", YEAR, itemizes)
    child = parent.get_branch("child")
    drop_inherited_values(child)
    # Inputs survive: the situation's and the one set on the parent branch.
    np.testing.assert_array_equal(
        child.get_array("employment_income", YEAR),
        simulation.get_array("employment_income", YEAR),
    )
    np.testing.assert_array_equal(child.get_array("tax_unit_itemizes", YEAR), itemizes)
    # Calculated values are gone, and are calculated again from the inputs.
    assert child.get_array("income_tax", YEAR) is None
    assert child.get_array("taxable_income", YEAR) is None
    np.testing.assert_allclose(
        child.calculate("taxable_income", YEAR),
        _fresh(households, "taxable_income", {"tax_unit_itemizes": itemizes}),
        atol=0.01,
    )
