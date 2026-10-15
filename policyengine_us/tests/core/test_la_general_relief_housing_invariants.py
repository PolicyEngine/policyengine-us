"""Properties of the 2024 LA GR housing payment, contribution and subsidy paid."""

import numpy as np
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation


MONTH = "2024-01"
YEAR = "2024"
VARIABLES = (
    "la_general_relief_housing_subsidy",
    "la_general_relief_housing_subsidy_amount",
    "la_general_relief_housing_subsidy_paid",
    "la_general_relief_rent_contribution",
    "la_general_relief",
)

# married, GR eligible, housing-program eligible, monthly rent.
ROW = st.tuples(st.booleans(), st.booleans(), st.booleans(), st.integers(0, 1_500))
EDGE_ROWS = [
    (False, True, True, 0),
    (True, True, True, 0),
    (False, True, True, 1),
    (True, True, True, 1),
    (False, True, True, 99),
    (False, True, True, 100),
    (False, True, True, 101),
    (False, True, True, 500),
    (True, True, True, 199),
    (True, True, True, 200),
    (True, True, True, 201),
    (True, True, True, 1_000),
    (False, True, True, 575),
    (True, True, True, 1_150),
    (False, True, True, 1_500),
    (True, True, True, 1_500),
    (False, True, False, 600),
    (True, False, True, 600),
]
EDGE_OVERRIDE_ROWS = [
    (False, 600, 0),
    (False, 600, 100),
    (False, 600, 150),
    (False, 600, 37.001258850097656),
    (True, 1_200, 0),
    (True, 1_200, 200),
    (True, 1_200, 74.00251770019531),
]


@st.composite
def _override_row(draw):
    married = draw(st.booleans())
    rent = draw(st.integers(0, 1_500))
    contribution = draw(
        st.floats(
            min_value=0,
            max_value=200 if married else 100,
            allow_nan=False,
            allow_infinity=False,
            width=32,
        )
    )
    return married, rent, contribution


def _situation(rows, supplied_contributions=None):
    situation = {
        "people": {},
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "households": {},
    }
    for index, (married, gr_eligible, housing_eligible, rent) in enumerate(rows):
        # All generated states are valid: housing eligibility implies GR eligibility.
        housing_eligible = housing_eligible and gr_eligible
        members = [f"person_{index}_{i}" for i in range(2 if married else 1)]
        for member_index, member in enumerate(members):
            situation["people"][member] = {
                "age": {YEAR: 40},
                "rent": {YEAR: 12 * rent if member_index == 0 else 0},
            }
        group = f"group_{index}"
        situation["tax_units"][group] = {"members": members}
        situation["families"][group] = {
            "members": members,
            "is_married": {YEAR: married},
        }
        situation["spm_units"][group] = {
            "members": members,
            "la_general_relief_eligible": {MONTH: gr_eligible},
            "la_general_relief_housing_subsidy_eligible": {YEAR: housing_eligible},
            "la_general_relief_base_amount": {MONTH: 375 if married else 221},
        }
        if supplied_contributions is not None and index in supplied_contributions:
            situation["spm_units"][group]["la_general_relief_rent_contribution"] = {
                MONTH: supplied_contributions[index]
            }
        situation["households"][group] = {
            "members": members,
            "state_code": {YEAR: "CA"},
            "in_la": {YEAR: True},
        }
    return situation


def _calculate(situation, variables):
    simulation = Simulation(situation=situation)
    return {variable: simulation.calculate(variable, MONTH) for variable in variables}


@settings(max_examples=8, deadline=None, derandomize=True)
@given(
    generated_rows=st.lists(ROW, min_size=5, max_size=20),
    generated_overrides=st.lists(_override_row(), min_size=5, max_size=20),
)
def test_housing_payment_invariants(generated_rows, generated_overrides):
    rows = EDGE_ROWS + generated_rows
    n_rows = len(rows)
    # Put the rent comparison in the same vectorized population to avoid
    # another model setup. Only calculation-order isolation needs a fresh sim.
    raised_rows = [
        (married, gr_eligible, housing_eligible, rent + 1_500)
        for married, gr_eligible, housing_eligible, rent in rows
    ]
    situation = _situation(rows + raised_rows)
    result = _calculate(situation, VARIABLES)
    # These dependencies must be acyclic for either requested variable order.
    reverse_result = _calculate(situation, VARIABLES[::-1])
    for variable in VARIABLES:
        np.testing.assert_array_equal(result[variable], reverse_result[variable])

    married = np.array([row[0] for row in rows])
    gr_eligible = np.array([row[1] for row in rows])
    housing_eligible = np.array([row[1] and row[2] for row in rows])
    rent = np.array([row[3] for row in rows], dtype=np.float32)
    # DPSS 46-103, Policy (#custom-title-f75ca3f760): single
    # 475 + 100 = 575; couple 950 + 200 = 1,150. PA 6182, page 1,
    # items 2-3: the contribution and additional subsidy go to the landlord.
    contribution_schedule = np.where(married, 200, 100)
    subsidy_schedule = np.where(married, 950, 475)
    total_schedule = np.where(married, 1_150, 575)
    expected_subsidy_amount = np.where(
        housing_eligible, np.minimum(rent, subsidy_schedule), 0
    )
    expected_subsidy = np.where(housing_eligible, np.minimum(rent, total_schedule), 0)
    expected_contribution = np.where(expected_subsidy > 0, contribution_schedule, 0)
    # Budget the remaining rent independently of the payment formula:
    # $500 single rent - $100 contribution = $400 additional subsidy;
    # $1,000 couple rent - $200 contribution = $800 additional subsidy.
    expected_paid = np.where(
        housing_eligible,
        np.minimum(np.maximum(rent - contribution_schedule, 0), subsidy_schedule),
        0,
    )
    expected_cash = np.where(
        gr_eligible, np.where(married, 375, 221) - expected_contribution, 0
    )

    subsidy_amount = result["la_general_relief_housing_subsidy_amount"][:n_rows]
    subsidy = result["la_general_relief_housing_subsidy"][:n_rows]
    contribution = result["la_general_relief_rent_contribution"][:n_rows]
    paid = result["la_general_relief_housing_subsidy_paid"][:n_rows]
    np.testing.assert_array_equal(subsidy_amount, expected_subsidy_amount)
    np.testing.assert_array_equal(subsidy, expected_subsidy)
    np.testing.assert_array_equal(contribution, expected_contribution)
    np.testing.assert_array_equal(paid, expected_paid)
    np.testing.assert_array_equal(result["la_general_relief"][:n_rows], expected_cash)
    assert np.all((subsidy_amount >= 0) & (subsidy_amount <= rent))
    assert np.all(subsidy_amount <= subsidy_schedule)
    assert np.all((subsidy >= 0) & (subsidy <= rent))
    assert np.all(subsidy <= total_schedule)
    assert np.all((paid >= 0) & (paid <= subsidy))
    assert np.all(paid <= subsidy_amount)
    assert np.all(contribution[~housing_eligible | (rent == 0)] == 0)
    # Retain the fixed contribution even below $100/$200 rent. Additional
    # subsidy is zero there; full reconciliation requires enough payment
    # to cover the contribution.
    covers_contribution = subsidy >= contribution
    np.testing.assert_array_equal(
        paid[covers_contribution] + contribution[covers_contribution],
        subsidy[covers_contribution],
    )
    assert np.all(paid[~covers_contribution] == 0)

    # Increasing rent cannot reduce housing payment; all eligible units saturate
    # at the scheduled subsidy plus contribution when rent exceeds that sum.
    raised_subsidy = result["la_general_relief_housing_subsidy"][n_rows:]
    assert np.all(raised_subsidy >= subsidy)
    np.testing.assert_array_equal(
        raised_subsidy, np.where(housing_eligible, total_schedule, 0)
    )
    raised_paid = result["la_general_relief_housing_subsidy_paid"][n_rows:]
    assert np.all(raised_paid >= paid)
    np.testing.assert_array_equal(
        raised_paid, np.where(housing_eligible, subsidy_schedule, 0)
    )

    override_rows = EDGE_OVERRIDE_ROWS + generated_overrides
    n_overrides = len(override_rows)
    raised_override_rows = [
        (married, rent + 1_500, contribution)
        for married, rent, contribution in override_rows
    ]
    # Keep overrides in a fresh eligible population: supplying a variable for
    # only some units would give its default value to all remaining units.
    override_situation_rows = [
        (married, True, True, rent)
        for married, rent, _ in override_rows + raised_override_rows
    ]
    supplied_contributions = {
        index: contribution
        for index, (_, _, contribution) in enumerate(
            override_rows + raised_override_rows
        )
    }
    override_result = _calculate(
        _situation(override_situation_rows, supplied_contributions), VARIABLES
    )
    override_married = np.array([row[0] for row in override_rows])
    override_rent = np.array([row[1] for row in override_rows], dtype=np.float32)
    override_contribution = np.array(
        [row[2] for row in override_rows], dtype=np.float32
    )
    override_subsidy_schedule = np.where(override_married, 950, 475).astype(np.float32)
    expected_override_amount = np.minimum(override_rent, override_subsidy_schedule)
    expected_override_payment = np.minimum(
        override_rent, expected_override_amount + override_contribution
    )
    expected_override_cash = (
        np.where(override_married, 375, 221).astype(np.float32) - override_contribution
    )
    expected_override_paid = np.minimum(
        np.maximum(override_rent - override_contribution, 0),
        override_subsidy_schedule,
    )
    np.testing.assert_array_equal(
        override_result["la_general_relief_housing_subsidy_amount"][:n_overrides],
        expected_override_amount,
    )
    np.testing.assert_array_equal(
        override_result["la_general_relief_rent_contribution"][:n_overrides],
        override_contribution,
    )
    np.testing.assert_array_equal(
        override_result["la_general_relief_housing_subsidy"][:n_overrides],
        expected_override_payment,
    )
    np.testing.assert_array_equal(
        override_result["la_general_relief"][:n_overrides], expected_override_cash
    )
    override_paid = override_result["la_general_relief_housing_subsidy_paid"][
        :n_overrides
    ]
    override_payment = override_result["la_general_relief_housing_subsidy"][
        :n_overrides
    ]
    # Adding and subtracting supplied float32 contributions can move the
    # residual by one ULP (e.g. 475.0000305 instead of 475).
    np.testing.assert_allclose(override_paid, expected_override_paid, rtol=0, atol=1e-4)
    assert np.all((override_paid >= 0) & (override_paid <= override_payment))
    assert np.all(override_paid <= expected_override_amount + 1e-4)
    override_covers_contribution = override_payment >= override_contribution
    np.testing.assert_allclose(
        override_paid[override_covers_contribution]
        + override_contribution[override_covers_contribution],
        override_payment[override_covers_contribution],
        rtol=0,
        atol=1e-4,
    )
    assert np.all(override_paid[~override_covers_contribution] == 0)
    raised_override_paid = override_result["la_general_relief_housing_subsidy_paid"][
        n_overrides:
    ]
    assert np.all(raised_override_paid >= override_paid)
    np.testing.assert_allclose(
        raised_override_paid, override_subsidy_schedule, rtol=0, atol=1e-4
    )
