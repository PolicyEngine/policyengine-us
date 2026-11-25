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
entity or with other ``ETERNITY`` storage than the baseline's variable has: a
kept holder hands the arm the reform's input in place of its formula. A
dropped holder takes its inputs with it, so where the caller gave such a
variable an input, the rebuild raises a ``ValueError`` naming the variable
rather than calculate it in place of the input.

Invariants: under a reform that changes nothing, the reform and its baseline
arm compute what a simulation with no reform computes, for every household,
whether a situation or a dataset of raw columns supplies the inputs. Under any
reform, each holder in either arm suits that arm's definition of its variable.
Under a reform that stores a variable apart from baseline policy, an input
given for it at construction, through a dataset or a situation, raises by
name. A branch that subsamples reads an arm built on its own sample.

One limit is pinned here too. Where core builds the arm, in ``subsample``, it
has already dropped such a holder and its recorded inputs, so an input set
after construction and then subsampled raises nothing: the new arm calculates
the variable, as on main.
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


SUBSIDY = "child_care_subsidies"
EXPENSE = "spm_unit_capped_work_childcare_expenses"
REFUSAL = f"Baseline policy cannot hold the input given for {SUBSIDY}"


def with_subsidy(subsidy):
    """The situation, with a child care subsidy given on the SPM unit."""
    given = situation()
    given["spm_units"]["spm_unit"][SUBSIDY] = subsidy
    return given


def subsidy_for_all_time_from_a_dataset():
    return Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], eternal_subsidy=500),
        reform=StoreSubsidiesForAllTime,
    )


def subsidy_for_the_year_from_a_dataset():
    return Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies={YEAR: [500]}),
        reform=StoreSubsidiesForAllTime,
    )


def subsidy_for_all_time_in_a_situation():
    return Simulation(
        situation=with_subsidy({"ETERNITY": 500}), reform=StoreSubsidiesForAllTime
    )


def subsidy_for_the_year_in_a_situation():
    return Simulation(
        situation=with_subsidy({YEAR: 500}), reform=StoreSubsidiesForAllTime
    )


@pytest.mark.parametrize(
    "build",
    [
        subsidy_for_all_time_from_a_dataset,
        subsidy_for_the_year_from_a_dataset,
        subsidy_for_all_time_in_a_situation,
        subsidy_for_the_year_in_a_situation,
    ],
)
def test_the_arm_refuses_a_subsidy_the_reform_stores_for_all_time(build):
    """New York's first family enters with a $500 subsidy, for all time or for
    2026, under a reform that stores ``child_care_subsidies`` for all time.
    Baseline policy's yearly variable can't use the reform's holder, so the
    arm would drop the input and calculate a subsidy in its place: given for
    2026, S0 would move from the $500 given to what baseline policy pays,
    though the subsidy paid hadn't changed. So construction refuses either
    input, naming the variable. The rebuild at the end of construction
    raises: where core builds the arm, it has already dropped the holder and
    its recorded input."""
    with pytest.raises(ValueError, match=REFUSAL) as refused:
        build()
    assert "_rebuild_baseline_branch" in [entry.name for entry in refused.traceback]


def test_an_input_set_after_construction_is_calculated_after_a_subsample():
    """The stated limit. Both runs read two New York families, and the sample
    keeps the second, the family a plain run pays more than $500. After
    construction the reform gets a $500 subsidy, which it stores for all
    time. Its arm never sees an input set after construction, and the
    subsample raises nothing: core drops the reform's holder from the arm it
    builds, so that arm calculates the subsidy, as on main. Construction's
    rebuild first drops the reform's empty holder for all time from the
    arm."""
    families = (FAMILIES[1], FAMILIES[0])
    simulations = [
        Microsimulation(
            dataset=dataset((NEW_YORK,), families, weights=(0, 1)), reform=reform
        )
        for reform in (None, StoreSubsidiesForAllTime)
    ]
    plain, reformed = simulations
    for simulation in (reformed, reformed.baseline):
        assert_holders_suit_their_variables(simulation)
    reformed.set_input(SUBSIDY, YEAR, [500, 500])
    for simulation in simulations:
        simulation.subsample(n=1)
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
        assert simulation.calculate("household_id", YEAR).values.tolist() == [1]
    calculated = value(plain, SUBSIDY)
    assert calculated[0] > 500
    np.testing.assert_allclose(value(arm, SUBSIDY), calculated, atol=TOLERANCE)
    np.testing.assert_allclose(value(reformed, SUBSIDY), [500])


STANDARD_DEDUCTION = Reform.from_dict(
    {"gov.irs.deductions.standard.amount.SINGLE": {"2026-01-01.2100-12-31": 20_000}},
    country_id="us",
)


def two_new_york_earners():
    """Two single earners in New York who each paid $500 for care. Only the
    second weighs anything, and each has its own subsidy."""
    columns = {
        "person_id": [0, 1],
        **{f"{entity}_id": [0, 1] for entity in ("household", "tax_unit")},
        **{f"{entity}_id": [0, 1] for entity in ("spm_unit", "family")},
        "marital_unit_id": [0, 1],
        f"age__{YEAR}": [40, 40],
        f"employment_income__{YEAR}": [80_000, 80_000],
        f"is_tax_unit_head__{YEAR}": [True, True],
        f"is_household_head__{YEAR}": [True, True],
        f"state_fips__{YEAR}": [NEW_YORK, NEW_YORK],
        f"household_weight__{YEAR}": [0.0, 1.0],
        f"{SUBSIDY}__{YEAR}": [100.0, 200.0],
        f"spm_unit_pre_subsidy_childcare_expenses__{YEAR}": [500.0, 500.0],
    }
    return Dataset.from_dataframe(pd.DataFrame(columns), time_period=YEAR)


def test_a_subsampled_branch_reads_an_arm_on_its_own_sample():
    """A branch shares its parent's arm, and core rebuilds only the arm a
    simulation holds in ``branches["baseline"]``. So a branch that
    subsampled kept the parent's arm, on both households, and the dataset
    rule, which reads S0 from that arm, raised on the size mismatch. Now the
    branch reads an arm on its own sample and gets the expense a subsample
    of the reform itself gets, $500, while the parent keeps its arm."""
    top = Microsimulation(dataset=two_new_york_earners(), reform=STANDARD_DEDUCTION)
    top.subsample(n=1, seed=0)
    expected = value(top, EXPENSE)
    np.testing.assert_allclose(expected, [500])

    parent = Microsimulation(dataset=two_new_york_earners(), reform=STANDARD_DEDUCTION)
    arm = parent.baseline
    branch = parent.get_branch("trial")
    assert branch.baseline is arm
    branch.subsample(n=1, seed=0)
    own_arm = branch.baseline
    assert own_arm is not arm
    assert own_arm is branch.branches["baseline"]
    assert own_arm.baseline is None
    assert own_arm.tax_benefit_system.simulation is own_arm
    np.testing.assert_allclose(value(own_arm, SUBSIDY), [200])
    np.testing.assert_allclose(value(branch, EXPENSE), expected)

    assert parent.baseline is arm
    assert arm.tax_benefit_system.simulation is arm
    np.testing.assert_allclose(value(arm, SUBSIDY), [100, 200])
    np.testing.assert_allclose(value(parent, EXPENSE), [500, 500])
