"""Sample rent-classification invariants in one vectorized engine batch per draw.

Wis. Stat. 71.07(9)(a)4 assigns each claimant their own qualified paid rent.
A complete classification must ignore unrelated generic rent, stay within its
own tax unit, and add across payers. Each Hypothesis draw creates one Simulation
for all original, perturbed and combined units, reusing the package's loaded
system. Ordinary source-derived amounts remain in variable-named YAML tests.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = "2025"


def _batch(specs):
    situation = {
        "people": {},
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    comparisons = []

    def add_home(name, units, heat_included):
        home_members = []
        for suffix, people in units:
            unit_id = f"{name}_{suffix}"
            members = []
            for index, (with_heat, without_heat, generic_rent) in enumerate(people):
                person_id = f"{unit_id}_{index}"
                situation["people"][person_id] = {
                    "age": {YEAR: 40},
                    "is_tax_unit_head": {YEAR: index == 0},
                    "is_tax_unit_spouse": {YEAR: index == 1},
                    "is_tax_unit_dependent": {YEAR: False},
                    "rent": {YEAR: generic_rent},
                    "real_estate_taxes": {YEAR: 0},
                    "wi_property_tax_credit_rent_with_heat": {YEAR: with_heat},
                    "wi_property_tax_credit_rent_without_heat": {YEAR: without_heat},
                }
                members.append(person_id)
            situation["tax_units"][unit_id] = {
                "members": members,
                "filing_status": {YEAR: "JOINT" if len(members) == 2 else "SINGLE"},
            }
            situation["marital_units"][unit_id] = {"members": members}
            situation["families"][unit_id] = {"members": members}
            home_members.extend(members)
        situation["households"][name] = {
            "members": home_members,
            "state_code": {YEAR: "WI"},
        }
        situation["spm_units"][name] = {
            "members": home_members,
            "heat_expense_included_in_rent": {YEAR: heat_included},
        }

    for index, (with_heat, without_heat, other_with, other_without, extra) in enumerate(
        specs
    ):
        first = (with_heat, without_heat, with_heat + without_heat + extra)
        other = (other_with, other_without, other_with + other_without + extra)
        base = f"base_{index}"
        changed = f"changed_{index}"
        combined = f"combined_{index}"
        add_home(base, [("a", [first]), ("b", [other])], True)
        add_home(
            changed,
            [
                ("a", [(with_heat, without_heat, first[2] + extra + 1)]),
                ("b", [(other_with + extra + 1, other_without, other[2] + extra + 1)]),
            ],
            False,
        )
        add_home(combined, [("joint", [first, other])], True)
        comparisons.append(
            (f"{base}_a", f"{base}_b", f"{changed}_a", f"{combined}_joint")
        )
    return situation, comparisons


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    st.lists(
        st.tuples(
            st.integers(1, 18_000),
            st.integers(0, 18_000),
            st.integers(0, 18_000),
            st.integers(0, 18_000),
            st.integers(0, 20_000),
        ),
        min_size=2,
        max_size=8,
    )
)
def test_wi_rent_classification_is_local_additive_and_ignores_generic_rent(specs):
    situation, comparisons = _batch(specs)
    simulation = Simulation(situation=situation)
    amount = simulation.calculate(
        "wi_property_tax_credit_rent_constituting_property_taxes", YEAR
    )
    available = simulation.calculate(
        "wi_property_tax_credit_rent_inputs_available", YEAR
    )
    potential = simulation.calculate("wi_property_tax_credit_potential", YEAR)
    ids = {
        unit_id: index
        for index, unit_id in enumerate(simulation.populations["tax_unit"].ids)
    }

    assert np.all(available)
    assert np.all(amount >= 0)
    assert np.all(potential >= 0)
    # Wis. Stat. 71.07(9)(b), ordinary single and joint ceiling.
    assert np.all(potential <= 300)
    for first, other, changed, combined in comparisons:
        assert amount[ids[first]] > 0
        np.testing.assert_allclose(
            amount[ids[first]], amount[ids[changed]], atol=0.01, rtol=0
        )
        np.testing.assert_allclose(
            potential[ids[first]], potential[ids[changed]], atol=0.01, rtol=0
        )
        np.testing.assert_allclose(
            amount[ids[combined]],
            amount[ids[first]] + amount[ids[other]],
            atol=0.01,
            rtol=0,
        )
