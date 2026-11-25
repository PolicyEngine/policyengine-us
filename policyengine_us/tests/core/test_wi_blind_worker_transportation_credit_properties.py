"""Entity locality and credit priority over generated, vectorized tax units.

Why Python: YAML pins source arithmetic; this changes arbitrary neighboring
units and a claimant's later credits while holding that claimant's facts and
preceding liability fixed. All six units share one household, so a mistaken
household aggregation can leak across real tax-unit memberships. This also
checks ordered-credit conservation and priority across generated payments and
liabilities, without reproducing the transportation percentage/cap formula.

Cost budget: one genuine Hypothesis function, four generated examples, one
vectorized Simulation of six tax units per example, using the package TBS.
No new CountryTaxBenefitSystem construction, datasets, clones or reforms.
Root measures elapsed time and peak memory in the final admitted test batch;
these are design bounds, not measured performance claims.

Sources: Wis. Stat. 71.07(11), chapter 71 PDF page 56; computation order in
71.10(4), PDF page 58. Supplied payments are already source-qualified net
commute expenses. These fixtures do not classify reimbursement or ABLE funds.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

CREDIT = "wi_blind_worker_transportation_credit"
POTENTIAL = "wi_blind_worker_transportation_credit_potential"
PERSON_CREDIT = "wi_blind_worker_transportation_credit_person"
EXPENSES = "wi_blind_worker_qualifying_transportation_expenses"
ORDERED = (
    "wi_itemized_deduction_credit",
    "wi_childcare_expense_credit",
    CREDIT,
    "wi_property_tax_credit",
    "wi_married_couple_credit",
)
OTHER_POTENTIALS = (
    "wi_itemized_deduction_credit_potential",
    "wi_childcare_expense_credit_potential",
    "wi_property_tax_credit_potential",
    "wi_married_couple_credit_potential",
)
TOLERANCE = 0.01

LAYOUT = st.fixed_dictionaries(
    {
        "status": st.sampled_from(
            ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]
        ),
        "payments": st.tuples(
            st.integers(-100, 10_000),
            st.integers(-100, 10_000),
            st.integers(-100, 10_000),
        ),
        "blind": st.tuples(st.booleans(), st.booleans(), st.booleans()),
        "liability": st.integers(0, 10_000),
        "prior": st.tuples(st.integers(0, 10_000), st.integers(0, 10_000)),
        "later": st.tuples(st.integers(0, 10_000), st.integers(0, 10_000)),
    }
)


def _situation(units, year):
    situation = {
        "people": {},
        "tax_units": {},
        "marital_units": {},
        "households": {},
    }
    nonclaimant_indices = []
    for index, unit in enumerate(units):
        roles = [("HEAD", 47, 0)]
        if unit["status"] == "JOINT":
            roles.append(("SPOUSE", 45, 1))
        roles.append(("DEPENDENT", 19, 2))
        members, couple = [], []
        for role, age, slot in roles:
            name = f"person{len(situation['people']) + 1}"
            if role == "DEPENDENT":
                nonclaimant_indices.append(len(situation["people"]))
            else:
                couple.append(name)
            situation["people"][name] = {
                "age": {year: age},
                "tax_unit_role_input": {year: role},
                "is_blind": {year: unit["blind"][slot]},
                "employment_income": {year: 0},
                EXPENSES: {year: unit["payments"][slot]},
            }
            members.append(name)
            if role == "DEPENDENT":
                situation["marital_units"][f"dependent{index}"] = {"members": [name]}
        situation["marital_units"][f"filers{index}"] = {"members": couple}
        other = dict(zip(OTHER_POTENTIALS, unit["prior"] + unit["later"]))
        situation["tax_units"][f"tax_unit{index}"] = {
            "members": members,
            "filing_status": {year: unit["status"]},
            "wi_income_tax_before_credits": {year: unit["liability"]},
            **{variable: {year: amount} for variable, amount in other.items()},
        }
    situation["households"]["household"] = {
        "members": list(situation["people"]),
        "state_code": {year: "WI"},
    }
    return situation, nonclaimant_indices


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    year=st.sampled_from([2024, 2025]),
    anchor=LAYOUT,
    left_neighbors=st.lists(LAYOUT, min_size=2, max_size=2),
    right_neighbors=st.lists(LAYOUT, min_size=2, max_size=2),
    changed_later=st.tuples(st.integers(0, 10_000), st.integers(0, 10_000)),
)
def test_transportation_credit_is_local_and_conserves_ordered_liability(
    year, anchor, left_neighbors, right_neighbors, changed_later
):
    # Twin claimant units have the same payments, roles, blindness, liability
    # and preceding credits; only later credits and their neighbors change.
    twin = {**anchor, "later": changed_later}
    units = [anchor, *left_neighbors, twin, *right_neighbors]
    situation, nonclaimant_indices = _situation(units, year)
    simulation = Simulation(situation=situation, tax_benefit_system=system)

    def calc(variable):
        return np.asarray(simulation.calculate(variable, year), dtype=float)

    person_credit = calc(PERSON_CREDIT)
    potential = calc(POTENTIAL)
    applied = np.column_stack([calc(variable) for variable in ORDERED])
    available = np.array([unit["liability"] for unit in units], dtype=float)
    potential_rows = np.array(
        [
            unit["prior"] + (potential[i],) + unit["later"]
            for i, unit in enumerate(units)
        ],
        dtype=float,
    )

    assert np.all(person_credit >= -TOLERANCE)
    assert np.all(person_credit <= 1_500 + TOLERANCE)
    np.testing.assert_array_equal(person_credit[nonclaimant_indices], 0)
    np.testing.assert_allclose(potential[0], potential[3], atol=TOLERANCE, rtol=0)
    np.testing.assert_allclose(applied[0, 2], applied[3, 2], atol=TOLERANCE, rtol=0)

    assert np.all(applied >= -TOLERANCE)
    assert np.all(applied <= potential_rows + TOLERANCE)
    np.testing.assert_allclose(
        applied.sum(axis=1),
        np.minimum(available, potential_rows.sum(axis=1)),
        atol=TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        calc("wi_non_refundable_credits"),
        applied.sum(axis=1),
        atol=TOLERANCE,
        rtol=0,
    )
    # A later credit can receive liability only after each predecessor's
    # potential has been met. This checks priority without computing a copy
    # of the transportation formula or the sequential capping helper.
    for row in range(len(units)):
        for credit_index in range(1, len(ORDERED)):
            if applied[row, credit_index] > TOLERANCE:
                np.testing.assert_allclose(
                    applied[row, :credit_index],
                    potential_rows[row, :credit_index],
                    atol=TOLERANCE,
                    rtol=0,
                )
