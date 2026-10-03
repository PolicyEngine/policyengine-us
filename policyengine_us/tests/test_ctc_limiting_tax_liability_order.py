"""CTC outputs must not depend on the order in which variables are requested.

`ctc_limiting_tax_liability` used to evaluate `income_tax_before_credits`
on a "no_salt" branch with `salt_deduction` set to zero. `get_branch`
copies every array the parent simulation has already cached, and
`set_input` on the branch does not invalidate values derived from the
overridden variable. So the branch returned the parent's SALT-inclusive
liability when `income_tax` had been requested first, and a liability with
no SALT (and, because itemization was pinned, no deduction at all) when
something reached `refundable_ctc` first (`medicaid`,
`household_net_income`, `spm_unit_net_income`, ...). policyengine.py
requests `medicaid` before `income_tax`, so its outputs differed from a
plain `Microsimulation` for liability-limited SALT itemizers.

Invariants checked here, for every household:

- Order independence: the CTC variables and `income_tax` are the same
  whichever variable is requested first.
- Section 26(a) limitation: `ctc_limiting_tax_liability` equals income tax
  before credits less the other non-refundable credits, floored at zero.
- Consistency with income tax: `ctc_value` equals the non-refundable CTC
  that actual liability absorbs plus the refundable CTC.
"""

from dataclasses import dataclass

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026

CTC_OUTPUTS = [
    "ctc_limiting_tax_liability",
    "refundable_ctc",
    "non_refundable_ctc",
    "ctc_value",
    "income_tax",
]

# Married couple in New York, one earner with $50,000 of wages, two
# children, $40,000 of property tax. SALT ($40,400 cap) exceeds the
# standard deduction, so taxable income is $9,600 and tax before credits
# is $960, well below the $4,400 CTC.
NY_SALT_ITEMIZER = {
    "people": {
        "head": {
            "age": 40,
            "employment_income": {YEAR: 50_000},
            "real_estate_taxes": {YEAR: 40_000},
        },
        "spouse": {"age": 40},
        "child1": {"age": 5},
        "child2": {"age": 8},
    },
    "tax_units": {"tax_unit": {"members": ["head", "spouse", "child1", "child2"]}},
    "households": {
        "household": {
            "members": ["head", "spouse", "child1", "child2"],
            "state_code": "NY",
        }
    },
}

FIRST_REQUESTS = [
    "income_tax",
    "ctc_limiting_tax_liability",
    "refundable_ctc",
    "ctc_value",
    "medicaid",
    "household_net_income",
    "spm_unit_net_income",
    "state_income_tax",
]


def _outputs(situation, first_variable, variables=CTC_OUTPUTS):
    sim = Simulation(situation=situation)
    sim.calculate(first_variable, YEAR)
    return {variable: sim.calculate(variable, YEAR) for variable in variables}


@pytest.mark.parametrize("first_variable", FIRST_REQUESTS)
def test_salt_itemizer_ctc_is_limited_by_actual_liability(first_variable):
    out = _outputs(NY_SALT_ITEMIZER, first_variable)
    # 26 USC 26(a): nonrefundable credits are limited to regular tax
    # liability, here $960 after the SALT deduction.
    assert out["ctc_limiting_tax_liability"][0] == pytest.approx(960)
    # 26 USC 24(d)(1): min($4,400 - $960, 2 x $1,700, 15% x ($50,000 -
    # $2,500)) = $3,400.
    assert out["refundable_ctc"][0] == pytest.approx(3_400)
    assert out["ctc_value"][0] == pytest.approx(960 + 3_400)


@dataclass(frozen=True)
class Household:
    married: bool
    children: int
    wages: int
    property_tax: int
    state: str


# Includes states whose income tax reads federal CTC or federal income tax
# variables (AL, CO, IA, MT, NY, OK, OR), where a dependency cycle through the
# SALT deduction would surface as a CycleError.
households = st.builds(
    Household,
    married=st.booleans(),
    children=st.integers(min_value=0, max_value=3),
    wages=st.integers(min_value=0, max_value=250).map(lambda k: k * 1_000),
    property_tax=st.integers(min_value=0, max_value=60).map(lambda k: k * 1_000),
    state=st.sampled_from(
        ["NY", "NJ", "CA", "CO", "OK", "IA", "AL", "MT", "OR", "MD", "TX"]
    ),
)


def _situation(batch):
    people, tax_units, spm_units, families, marital_units, hhs = ({} for _ in range(6))
    for i, h in enumerate(batch):
        head = f"head_{i}"
        adults = [head]
        people[head] = {
            "age": 40,
            "employment_income": {YEAR: h.wages},
            "real_estate_taxes": {YEAR: h.property_tax},
        }
        if h.married:
            adults.append(f"spouse_{i}")
            people[f"spouse_{i}"] = {"age": 40}
        children = [f"child_{i}_{k}" for k in range(h.children)]
        for k, child in enumerate(children):
            people[child] = {"age": 2 + 5 * k}
            marital_units[f"marital_unit_{child}"] = {"members": [child]}
        members = adults + children
        marital_units[f"marital_unit_{i}"] = {"members": adults}
        tax_units[f"tax_unit_{i}"] = {"members": members}
        spm_units[f"spm_unit_{i}"] = {"members": members}
        families[f"family_{i}"] = {"members": members}
        hhs[f"household_{i}"] = {"members": members, "state_code": h.state}
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "families": families,
        "marital_units": marital_units,
        "households": hhs,
    }


@settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.lists(households, min_size=1, max_size=6))
def test_ctc_invariants_hold_in_every_request_order(batch):
    situation = _situation(batch)
    extra = ["income_tax_before_credits", "ctc"]
    reference = _outputs(situation, "income_tax", CTC_OUTPUTS + extra)
    for first_variable in ["refundable_ctc", "medicaid", "household_net_income"]:
        other = _outputs(situation, first_variable, CTC_OUTPUTS + extra)
        for variable in CTC_OUTPUTS + extra:
            np.testing.assert_allclose(
                other[variable],
                reference[variable],
                atol=0.01,
                err_msg=f"{variable} differs when {first_variable} is requested first",
            )

    sim = Simulation(situation=situation)
    credits = sim.tax_benefit_system.parameters(YEAR).gov.irs.credits.non_refundable
    other_credits = sum(
        sim.calculate(credit, YEAR)
        for credit in credits
        if credit != "non_refundable_ctc"
    )
    liability = np.maximum(0, reference["income_tax_before_credits"] - other_credits)
    np.testing.assert_allclose(
        reference["ctc_limiting_tax_liability"], liability, atol=0.01
    )
    delivered = (
        np.minimum(reference["non_refundable_ctc"], liability)
        + reference["refundable_ctc"]
    )
    np.testing.assert_allclose(reference["ctc_value"], delivered, atol=0.01)
