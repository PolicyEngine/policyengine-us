"""Property and differential tests for the CTC's tax-liability limit.

The model follows Schedule 8812 Credit Limit Worksheets A and B and the
Form 5695 Residential Clean Energy Credit Limit Worksheet. These tests check
it against the statute applied directly, which never mentions the worksheets:

- 26 U.S.C. 26(a) limits the aggregate of the subpart A credits to the tax.
- 26 U.S.C. 24(d)(1) refunds the lesser of the CTC (capped at $1,700 per
  qualifying child by 24(h)(5)) and the amount by which the aggregate subpart
  A credits would increase if the 26(a) limit rose by the earned income
  phase-in amount; the refunded amount reduces the non-refundable CTC.
- 26 U.S.C. 25D(c) orders the residential clean energy credit after every
  other subpart A credit.

Households are married or single filers in Texas who take the standard
deduction, so the CTC limit's no-SALT liability equals actual liability.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025

OUTPUTS = [
    "income_tax_before_credits",
    "tax_unit_itemizes",
    "ctc",
    "ctc_refundable_maximum",
    "ctc_phase_in",
    "energy_efficient_home_improvement_credit_potential",
    "energy_efficient_home_improvement_credit",
    "residential_clean_energy_credit_potential",
    "residential_clean_energy_credit_credit_limit",
    "residential_clean_energy_credit",
    "ctc_tax_liability_after_preceding_credits",
    "ctc_credit_limit_worksheet_b_applies",
    "ctc_non_refundable_minimum",
    "ctc_limiting_tax_liability",
    "refundable_ctc",
    "non_refundable_ctc",
    "income_tax_capped_non_refundable_credits",
    "income_tax_before_refundable_credits",
]


def build_situation(households):
    people, tax_units, units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {YEAR: 40},
            "employment_income": {YEAR: h["wages"]},
            "taxable_interest_income": {YEAR: h["interest"]},
        }
        members = [head]
        units[f"marital_unit_{i}"] = {"members": [head]}
        if h["married"]:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {YEAR: 40}}
            members.append(spouse)
            units[f"marital_unit_{i}"]["members"].append(spouse)
        for j, age in enumerate(h["dependent_ages"]):
            dependent = f"dependent_{i}_{j}"
            people[dependent] = {"age": {YEAR: age}}
            members.append(dependent)
            units[f"marital_unit_{i}_{j}"] = {"members": [dependent]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "solar_electric_property_expenditures": {YEAR: h["solar"]},
            "energy_efficient_home_improvement_credit_potential": {
                YEAR: h["home_improvement_credit"]
            },
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": units,
        **groups,
    }


def calculate(households):
    simulation = Simulation(situation=build_situation(households))
    return {
        variable: np.asarray(simulation.calculate(variable, YEAR))
        for variable in OUTPUTS
    }


def statutory_reference(r):
    """Apply 26 U.S.C. 24(d)(1), 25D(c) and 26(a) directly.

    The inputs this change does not touch come from the model: income tax
    before credits, each credit before the 26(a) limit, the per-child refund
    cap and the earned income (or Social Security tax) increase.
    """
    liability = r["income_tax_before_credits"]
    # The only other credit in these households is the energy efficient home
    # improvement credit, which precedes both (Form 5695, line 31).
    prior_potential = r["energy_efficient_home_improvement_credit_potential"]
    prior = r["energy_efficient_home_improvement_credit"]
    ctc = r["ctc"]
    potential = r["residential_clean_energy_credit_potential"]

    def aggregate(limit):
        # Subpart A credits allowed under a 26(a) limit, before 24(d).
        return np.minimum(np.maximum(limit, 0), prior_potential + ctc + potential)

    increase = aggregate(liability + r["ctc_phase_in"]) - aggregate(liability)
    refundable = np.minimum(np.minimum(r["ctc_refundable_maximum"], ctc), increase)
    non_refundable_ctc = ctc - refundable
    liability_after_prior = np.maximum(liability - prior, 0)
    ctc_used = np.minimum(non_refundable_ctc, liability_after_prior)
    residential_clean_energy = np.minimum(potential, liability_after_prior - ctc_used)
    return {
        "refundable_ctc": refundable,
        "residential_clean_energy_credit": residential_clean_energy,
        "income_tax_capped_non_refundable_credits": (
            prior + ctc_used + residential_clean_energy
        ),
    }


def assert_matches_statute(r):
    assert not r["tax_unit_itemizes"].any()
    expected = statutory_reference(r)
    for variable, values in expected.items():
        np.testing.assert_allclose(r[variable], values, atol=0.01, err_msg=variable)


def assert_invariants(r):
    tol = 0.01
    line_3 = r["ctc_tax_liability_after_preceding_credits"]
    line_5 = r["ctc_limiting_tax_liability"]
    rce = r["residential_clean_energy_credit"]
    worksheet_b = r["ctc_credit_limit_worksheet_b_applies"]
    # Worksheet A: 0 <= line 5 <= line 3 <= income tax before credits.
    assert (line_5 >= 0).all()
    assert (line_5 <= line_3 + tol).all()
    assert (line_3 <= np.maximum(r["income_tax_before_credits"], 0) + tol).all()
    # With Worksheet B, line 5 = line 3 - the residential clean energy credit;
    # without it, line 5 = line 3.
    np.testing.assert_allclose(
        line_5, np.where(worksheet_b, line_3 - rce, line_3), atol=tol
    )
    # The residential clean energy credit never exceeds its potential or limit.
    assert (rce <= r["residential_clean_energy_credit_potential"] + tol).all()
    assert (rce <= r["residential_clean_energy_credit_credit_limit"] + tol).all()
    # Section 24(d)(1): the refund never exceeds the per-child cap, the credit
    # or the phase-in amount.
    cap = np.minimum(
        np.minimum(r["ctc_refundable_maximum"], r["ctc"]),
        np.maximum(r["ctc_phase_in"], 0),
    )
    assert (r["refundable_ctc"] <= cap + tol).all()
    # Section 26(a): non-refundable credits never exceed the tax.
    assert (
        r["income_tax_capped_non_refundable_credits"]
        <= r["income_tax_before_credits"] + tol
    ).all()


GRID = [
    {
        "married": married,
        "dependent_ages": ages,
        "wages": wages,
        "interest": interest,
        "solar": solar,
        "home_improvement_credit": home_improvement_credit,
    }
    for married in (True, False)
    for ages in ([], [5], [5, 8], [3, 6, 9], [17], [5, 17])
    for wages in (0, 12_000, 30_000, 60_000, 120_000)
    for interest in (0, 40_000)
    for solar in (0, 2_000, 10_000)
    for home_improvement_credit in (0, 300)
]


def test_grid_matches_statute_and_invariants():
    r = calculate(GRID)
    assert_matches_statute(r)
    assert_invariants(r)
    # The grid exercises every branch of Worksheet B.
    assert r["ctc_credit_limit_worksheet_b_applies"].any()
    assert (~r["ctc_credit_limit_worksheet_b_applies"] & (r["ctc"] > 0)).any()
    limited = r["residential_clean_energy_credit"] < (
        r["residential_clean_energy_credit_potential"] - 1
    )
    assert (limited & r["ctc_credit_limit_worksheet_b_applies"]).any()


household_strategy = st.fixed_dictionaries(
    {
        "married": st.booleans(),
        "dependent_ages": st.lists(st.integers(0, 18), max_size=4),
        "wages": st.integers(0, 200_000),
        "interest": st.integers(0, 100_000),
        "solar": st.integers(0, 40_000),
        "home_improvement_credit": st.integers(0, 1_200),
    }
)


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(household_strategy, min_size=1, max_size=25))
def test_random_households_match_statute_and_invariants(households):
    r = calculate(households)
    assert_matches_statute(r)
    assert_invariants(r)


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(household_strategy, min_size=1, max_size=15),
    st.integers(1, 20_000),
)
def test_more_residential_clean_energy_spending_never_raises_tax(households, extra):
    # Each household appears twice: with its spending and with more.
    more = [{**h, "solar": h["solar"] + extra} for h in households]
    r = calculate(households + more)
    tax = r["income_tax_before_refundable_credits"] - r["refundable_ctc"]
    n = len(households)
    assert (tax[n:] <= tax[:n] + 0.01).all()
