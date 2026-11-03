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
moves. Like core's branch, it drops each holder the reform built in another
entity or with other ``ETERNITY`` storage than the baseline's variable has.
A kept holder hands the arm the reform's input in place of its formula. A
dropped holder takes its inputs with it, so the arm then sets again each input
the reform received for a variable it stores apart from baseline policy,
wherever the baseline's definition can hold that input. Without that step, a
yearly subsidy the reform stores for all time left the arm calculating one.

Invariants: under a reform that changes nothing, the reform and its baseline
arm compute what a simulation with no reform computes, for every household,
whether a situation or a dataset of raw columns supplies the inputs. Under any
reform, each holder in either arm suits that arm's definition of its variable,
and the arm reads each dataset input that baseline policy can hold as a
simulation with no reform reads it, before and after subsampling.
"""

from itertools import product

import numpy as np
import pandas as pd
import pytest
from policyengine_core.data import Dataset
from policyengine_core.periods import ETERNITY
from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable

from policyengine_us import Microsimulation, Simulation
from policyengine_us.entities import SPMUnit
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    _baseline_measurement_branch,
)

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


class child_care_subsidies(Variable):
    # Stored for all time, where baseline policy calculates it each year.
    value_type = float
    entity = SPMUnit
    label = "Child care subsidies"
    definition_period = ETERNITY


class StoreSubsidiesForAllTime(Reform):
    def apply(self):
        self.update_variable(child_care_subsidies)


def dataset(
    states=STATE_FIPS,
    families=FAMILIES,
    eternal_subsidy=None,
    yearly_subsidies=None,
    weights=None,
):
    """A flat file with one household per state and family. ``yearly_subsidies``
    maps a year to each household's child care subsidy, and ``weights`` gives
    each household's weight."""
    columns = {}

    def add(name, parent, child):
        columns.setdefault(name, []).extend([parent, child])

    for unit, (fips, family) in enumerate(product(states, families)):
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
        weight = 1 if weights is None else weights[unit]
        add(f"household_weight__{YEAR}", weight, weight)
        if eternal_subsidy is not None:
            add("child_care_subsidies__eternity", eternal_subsidy, eternal_subsidy)
        for year, subsidies in (yearly_subsidies or {}).items():
            add(f"child_care_subsidies__{year}", subsidies[unit], subsidies[unit])
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


def value(simulation, variable, year=YEAR):
    return np.asarray(simulation.calculate(variable, year), dtype=float)


def values(simulation):
    return {
        variable: value(simulation, variable) for variable in PRE_RESPONSE + OUTPUTS
    }


def assert_holders_suit_their_variables(simulation):
    """Each holder sits in its variable's entity, with ``ETERNITY`` storage
    exactly when the simulation's own definition of the variable has it."""
    variables = simulation.tax_benefit_system.variables
    for population in simulation.populations.values():
        for name, holder in population._holders.items():
            variable = variables.get(name)
            assert holder.variable is variable, name
            assert variable.entity.key == population.entity.key, name
            assert holder._memory_storage.is_eternal == (
                variable.definition_period == ETERNITY
            ), name


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
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
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


def test_the_arm_calculates_what_the_reform_stores_for_all_time():
    """New York's first family enters with a $500 subsidy for all time, which
    the reform stores for all time. The baseline's yearly
    ``child_care_subsidies`` can hold no input for all time, so the arm drops
    the input and pays what a simulation with no reform pays. Keeping it gave
    the arm $500 as S0 where baseline policy pays $13,916.40, and left the
    reform's expense $13,416.40 low."""
    plain = Microsimulation(dataset=dataset((NEW_YORK,), FAMILIES[:1]))
    reformed = Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], eternal_subsidy=500),
        reform=StoreSubsidiesForAllTime,
    )
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)

    baseline_subsidy = value(plain, "child_care_subsidies")
    assert baseline_subsidy[0] > 500
    np.testing.assert_allclose(
        value(arm, "child_care_subsidies"), baseline_subsidy, atol=TOLERANCE
    )
    np.testing.assert_allclose(value(reformed, "child_care_subsidies"), 500)
    expense = "spm_unit_capped_work_childcare_expenses"
    np.testing.assert_allclose(
        value(arm, expense), value(plain, expense), atol=TOLERANCE
    )
    # The dataset rule moves the reported amount by the change in subsidy.
    expected = np.minimum(
        value(reformed, "spm_unit_work_expenses")
        + np.maximum(
            value(reformed, "spm_unit_pre_subsidy_childcare_expenses")
            - (500 - baseline_subsidy),
            0,
        ),
        value(reformed, "spm_unit_head_spouse_earned_cap"),
    )
    np.testing.assert_allclose(value(reformed, expense), expected, atol=TOLERANCE)


def test_the_arm_sets_again_the_yearly_subsidies_the_reform_stores_for_all_time():
    """Both runs read the same dataset, which gives New York's first family a
    $400 child care subsidy in 2025 and $500 in 2026. The reform stores
    ``child_care_subsidies`` for all time, so it keeps one of them, and the
    arm drops that holder. The arm then sets both yearly inputs again and
    reads each year's as a simulation with no reform does. Before, it
    calculated the 2026 subsidy, and S0 rose to $13,916.40 though the subsidy
    paid had not changed."""
    subsidies = {2025: [400], YEAR: [500]}
    plain = Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies=subsidies)
    )
    reformed = Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies=subsidies),
        reform=StoreSubsidiesForAllTime,
    )
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
    for year, subsidy in subsidies.items():
        for simulation in (plain, arm):
            np.testing.assert_allclose(
                value(simulation, "child_care_subsidies", year), subsidy
            )
        # The reform's holder keeps the input it received last, for all time.
        np.testing.assert_allclose(value(reformed, "child_care_subsidies", year), 500)
    # S1 equals S0, so the reform reports the expense baseline policy reports.
    expense = "spm_unit_capped_work_childcare_expenses"
    for simulation in (reformed, arm):
        np.testing.assert_allclose(
            value(simulation, expense), value(plain, expense), atol=TOLERANCE
        )


def test_the_baseline_measurement_sets_again_the_yearly_subsidies():
    """The behavioural-response measurement branches the reform under baseline
    policy and drops the same holder, so it too sets each yearly input
    again."""
    subsidies = {2025: [400], YEAR: [500]}
    reformed = Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies=subsidies),
        reform=StoreSubsidiesForAllTime,
    )
    try:
        branch = _baseline_measurement_branch(reformed)
        assert_holders_suit_their_variables(branch)
        for year, subsidy in subsidies.items():
            np.testing.assert_allclose(
                value(branch, "child_care_subsidies", year), subsidy
            )
    finally:
        reformed.branches.pop(BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, None)


def test_subsampling_keeps_each_yearly_subsidy_for_the_arm():
    """Core subsamples by rebuilding the simulation from what its holders
    record, and the reform's holder for all time records neither year. The
    sample keeps only the second household, whose inputs the arm then reads
    for each year, as before subsampling. A subsample that fails before core
    rebuilds anything leaves the simulation's inputs, and those it kept, in
    place."""
    subsidies = {2025: [400, 600], YEAR: [500, 700]}
    reformed = Microsimulation(
        dataset=dataset(
            (NEW_YORK,), FAMILIES, yearly_subsidies=subsidies, weights=(0, 1)
        ),
        reform=StoreSubsidiesForAllTime,
    )
    with pytest.raises(ValueError, match="Either n or frac"):
        reformed.subsample()
    reformed.subsample(n=1)
    arm = reformed.baseline
    assert reformed.calculate("household_id", YEAR).values.tolist() == [1]
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
    for year, subsidy in subsidies.items():
        np.testing.assert_allclose(
            value(arm, "child_care_subsidies", year), subsidy[1:]
        )
        np.testing.assert_allclose(value(reformed, "child_care_subsidies", year), 700)
