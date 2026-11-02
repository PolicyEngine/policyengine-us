"""A child care subsidy pays for care.

Invariant, in every state and for any family: children with no child care bill
and no care hours draw no subsidy, so child_care_subsidies is 0. Vermont and New
Hampshire broke this until they gated their payments on care.

This sweeps all 51 programs at once. YAML can pin one family in one state, but it
can't assert one rule across every state and a generated family, and one
simulation holds all 51 households, so each example builds one model.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO "
    "MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()


def situation(earnings, child_ages, disabled):
    people, tax_units, spm_units, families, marital_units, households = (
        {} for _ in range(6)
    )
    for state in STATES:
        parent = f"{state}_parent"
        children = [f"{state}_child_{i}" for i in range(len(child_ages))]
        members = [parent, *children]
        people[parent] = {
            "age": {YEAR: 30},
            "employment_income": {YEAR: earnings},
            "weekly_hours_worked_before_lsr": {YEAR: 40},
            "weeks_worked": {YEAR: 52},
        }
        for child, age in zip(children, child_ages):
            people[child] = {
                "age": {YEAR: age},
                "is_disabled": {YEAR: disabled},
                "is_tax_unit_dependent": {YEAR: True},
            }
        tax_units[state] = {"members": members}
        families[state] = {"members": members}
        marital_units[state] = {"members": [parent]}
        spm_units[state] = {
            "members": members,
            "spm_unit_pre_subsidy_childcare_expenses": {YEAR: 0},
            "meets_ccdf_activity_test": {YEAR: True},
        }
        households[state] = {"members": members, "state_name": {YEAR: state}}
    return {
        "people": people,
        "tax_units": tax_units,
        "families": families,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "households": households,
    }


@settings(max_examples=8, deadline=None)
@given(
    earnings=st.integers(0, 60_000),
    child_ages=st.lists(st.integers(0, 12), min_size=1, max_size=2),
    disabled=st.booleans(),
)
def test_no_care_draws_no_subsidy(earnings, child_ages, disabled):
    simulation = Simulation(situation=situation(earnings, child_ages, disabled))
    subsidies = simulation.calculate("child_care_subsidies", YEAR)
    paying = {
        state: float(amount) for state, amount in zip(STATES, subsidies) if amount != 0
    }
    assert paying == {}
