"""A reform's baseline arm reads the inputs a simulation with no reform reads.

Core builds the arm inside its ``__init__``. The country simulations then move
the aggregates in ``PRE_RESPONSE_INPUTS``, such as ``employment_income`` and
``weekly_hours_worked``, to their pre-response variables and fill
``state_code`` from ``state_code_str``, and a branch keeps none of what its
parent stores later. Before PolicyEngine/policyengine-us#9698 the arm therefore
read 0 from the pre-response variables: under any reform it saw no hours
worked and paid no New York child care subsidy to a family that a simulation
with no reform paid one. Over a dataset the SPM expense moves by the change in
subsidy it reads from that arm, so the gap became a double count.
``system._rebuild_baseline_branch`` now branches the arm again after the
moves.

Invariant: under a reform that changes nothing, the reform and its baseline
arm compute what a simulation with no reform computes, for every household,
whether a situation or a dataset of raw columns supplies the inputs.
"""

from itertools import product

import numpy as np
import pandas as pd
from policyengine_core.data import Dataset
from policyengine_core.reforms import Reform

from policyengine_us import Microsimulation, Simulation

YEAR = 2026
TOLERANCE = 0.01
# Every state and DC, as state_name reads them.
STATE_FIPS = (
    *(1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23),
    *(24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41),
    *(42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56),
)
NEW_YORK = 36
# A parent and a child aged 3 in full-time care. Each tuple holds the parent's
# wages, self-employment income, long-term capital gains, weekly hours and
# Social Security retirement benefit, then what the unit paid for care.
FAMILIES = (
    (30_000, 0, 0, 40, 0, 14_000),
    (15_000, 3_000, 1_000, 20, 1_200, 6_000),
)
PRE_RESPONSE = (
    "employment_income_before_lsr",
    "self_employment_income_before_lsr",
    "weekly_hours_worked_before_lsr",
    "long_term_capital_gains_before_response",
)
OUTPUTS = (
    "child_care_subsidies",
    "spm_unit_capped_work_childcare_expenses",
    "social_security",
    "snap",
    "income_tax",
    "spm_unit_net_income",
    "household_net_income",
)


class NoChange(Reform):
    def apply(self):
        pass


def dataset():
    columns = {}

    def add(name, parent, child):
        columns.setdefault(name, []).extend([parent, child])

    for unit, (fips, family) in enumerate(product(STATE_FIPS, FAMILIES)):
        wages, self_employment, gains, hours, retirement, expenses = family
        add("person_id", 2 * unit, 2 * unit + 1)
        for entity in ("household", "tax_unit", "spm_unit", "family"):
            add(f"{entity}_id", unit, unit)
        add("marital_unit_id", 2 * unit, 2 * unit + 1)
        add(f"age__{YEAR}", 30, 3)
        add(f"employment_income__{YEAR}", wages, 0)
        add(f"self_employment_income__{YEAR}", self_employment, 0)
        add(f"long_term_capital_gains__{YEAR}", gains, 0)
        add(f"weekly_hours_worked__{YEAR}", hours, 0)
        add(f"social_security_retirement__{YEAR}", retirement, 0)
        add(f"is_tax_unit_head__{YEAR}", True, False)
        add(f"is_household_head__{YEAR}", True, False)
        add(f"is_tax_unit_dependent__{YEAR}", False, True)
        add(f"childcare_hours_per_day__{YEAR}", 0, 8)
        add(f"childcare_days_per_week__{YEAR}", 0, 5)
        add(f"childcare_attending_days_per_month__{YEAR}", 0, 21)
        add(f"spm_unit_pre_subsidy_childcare_expenses__{YEAR}", expenses, expenses)
        add(f"state_fips__{YEAR}", fips, fips)
        add(f"household_weight__{YEAR}", 1, 1)
    return Dataset.from_dataframe(pd.DataFrame(columns), time_period=YEAR)


def situation():
    """The first family in New York, naming its state only through
    state_code_str, with the second family's other income."""
    members = ["parent", "child"]
    return {
        "people": {
            "parent": {
                "age": {YEAR: 30},
                "employment_income": {YEAR: 30_000},
                "self_employment_income": {YEAR: 3_000},
                "long_term_capital_gains": {YEAR: 1_000},
                "weekly_hours_worked": {YEAR: 40},
                "social_security_retirement": {YEAR: 1_200},
                "is_tax_unit_head": {YEAR: True},
                "is_household_head": {YEAR: True},
            },
            "child": {
                "age": {YEAR: 3},
                "childcare_hours_per_day": {YEAR: 8},
                "childcare_days_per_week": {YEAR: 5},
                "childcare_attending_days_per_month": {YEAR: 21},
                "is_tax_unit_dependent": {YEAR: True},
            },
        },
        "tax_units": {"tax_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {
            "parent_marital_unit": {"members": ["parent"]},
            "child_marital_unit": {"members": ["child"]},
        },
        "spm_units": {
            "spm_unit": {
                "members": members,
                "spm_unit_pre_subsidy_childcare_expenses": {YEAR: 14_000},
            }
        },
        "households": {
            "household": {"members": members, "state_code_str": {YEAR: "NY"}}
        },
    }


def values(simulation):
    return {
        variable: np.asarray(simulation.calculate(variable, YEAR), dtype=float)
        for variable in PRE_RESPONSE + OUTPUTS
    }


def assert_both_arms_match(plain, reformed):
    arm = reformed.baseline
    assert reformed.branches["baseline"] is arm
    assert arm.parent_branch is reformed
    assert arm.baseline is None
    # The arm owns its policy, which names the arm rather than the one it
    # replaced.
    assert arm.tax_benefit_system is not reformed.tax_benefit_system
    assert arm.tax_benefit_system.simulation is arm
    # No calculation has run yet, so the arm holds only inputs, and no value
    # the reform's policy produced.
    assert arm.drop_computed_arrays() == 0
    expected = values(plain)
    for name, simulation in (("reform", reformed), ("baseline arm", arm)):
        for variable, array in values(simulation).items():
            np.testing.assert_allclose(
                array,
                expected[variable],
                atol=TOLERANCE,
                err_msg=f"{name}: {variable}",
            )
    return expected


def test_dataset_arms_match_a_simulation_with_no_reform():
    plain = Microsimulation(dataset=dataset())
    expected = assert_both_arms_match(
        plain, Microsimulation(dataset=dataset(), reform=NoChange)
    )
    states = plain.calculate("state_code", YEAR).values
    assert len(set(states)) == len(STATE_FIPS)
    # The comparison covers households these programs pay, New York's first
    # family among them, which the arm used to pay nothing.
    subsidies = expected["child_care_subsidies"]
    assert (subsidies > 0).sum() >= 10
    assert subsidies[STATE_FIPS.index(NEW_YORK) * len(FAMILIES)] > 0
    assert (expected["social_security"] > 0).any()


def test_situation_arms_match_a_simulation_with_no_reform():
    plain = Simulation(situation=situation())
    reformed = Simulation(situation=situation(), reform=NoChange)
    expected = assert_both_arms_match(plain, reformed)
    assert expected["child_care_subsidies"].sum() > 0
    for simulation in (plain, reformed, reformed.baseline):
        state = simulation.calculate("state_code", YEAR).decode_to_str()
        assert state.tolist() == ["NY"]
