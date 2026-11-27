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
name. A branch that subsamples reads an arm built on its own sample, under
baseline policy, even where the caller named one of its calculation branches
"baseline". A subsample that raises before core rebuilds the arm leaves what
the branch held under that name as it was. A simulation that is itself named
"baseline" and has an arm raises when asked to subsample, before it changes
anything. A snapshot of a dataset simulation, from ``export_source_inputs`` or
``extract_person``, reloads with the dataset's rule for the SPM child care
expense, in the reform and in its arm, and a dump of one restores with it; a
snapshot or dump without the dataset mark reloads as a household, and a mark
other than true or false raises. A marked reload's arm holds what the
source's arm held for each override: the dataset's value, or, where a caller
set a value on the reform after construction, what the arm kept.

One limit is pinned here too. Where core builds the arm, in ``subsample``, it
has already dropped such a holder and its recorded inputs, so an input set
after construction and then subsampled raises nothing: the new arm calculates
the variable, as on main.
"""

import json
from itertools import product

import numpy as np
import pandas as pd
import pytest
from policyengine_core.data import Dataset
from policyengine_core.periods import ETERNITY
from policyengine_core.reforms import Reform
from policyengine_core.tools import simulation_dumper
from policyengine_core.variables import Variable

from policyengine_us import Microsimulation, Simulation
from policyengine_us.entities import Person, SPMUnit
from policyengine_us.tools.social_security_inputs import (
    export_source_inputs,
    reload_source_inputs,
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
    given=None,
):
    """A flat file with one household per state and family. ``yearly_subsidies``
    maps a year to each household's child care subsidy, ``weights`` gives
    each household's weight, and ``given`` maps a variable to each household's
    value of it in 2026."""
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
        for name, given_values in (given or {}).items():
            add(f"{name}__{YEAR}", given_values[unit], given_values[unit])
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
    builds, so that arm calculates the subsidy, as on main."""
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


SSTB_INCOME = "sstb_self_employment_income"


class sstb_self_employment_income(Variable):
    # Stored for all time, where baseline policy stores it each year.
    value_type = float
    entity = Person
    label = "SSTB self-employment income"
    definition_period = ETERNITY


class StoreSSTBIncomeForAllTime(Reform):
    def apply(self):
        self.update_variable(sstb_self_employment_income)


def test_the_rebuild_drops_a_holder_the_reform_built_with_no_input():
    """Construction moves ``sstb_self_employment_income`` to its pre-response
    variable, so it asks the reform for that variable's holder even where the
    caller gave no input. Under a reform that stores the variable for all
    time, the reform then holds an empty holder for all time, and the arm
    branched after the moves copies it. With no input recorded, the guard has
    nothing to refuse, so the rebuild's own drop keeps that holder out of the
    arm."""
    reformed = Microsimulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1]), reform=StoreSSTBIncomeForAllTime
    )
    holder = reformed.populations["person"]._holders.get(SSTB_INCOME)
    assert holder is not None and holder._memory_storage.is_eternal
    assert SSTB_INCOME not in {key[0] for key in reformed._user_input_keys}
    arm = reformed.baseline
    assert SSTB_INCOME not in arm.populations["person"]._holders
    assert_holders_suit_their_variables(arm)


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


REPEAL = Reform.from_dict(
    {"gov.abolitions.child_care_subsidies": {"2026-01-01.2026-12-31": True}},
    country_id="us",
)
# What a subsample of the reform itself reads under REPEAL, keeping the second
# New York family: S0, and the expense, $6,000 reported plus the $6,000 lost.
SAMPLED_S0 = [6_000]
SAMPLED_EXPENSE = [12_000]


def new_york_families():
    """Both New York families. Only the second weighs anything."""
    return dataset((NEW_YORK,), FAMILIES, weights=(0, 1))


def repeals_the_subsidy(simulation):
    parameters = simulation.tax_benefit_system.parameters(f"{YEAR}-01-01")
    return bool(parameters.gov.abolitions.child_care_subsidies)


def households(simulation):
    return simulation.calculate("household_id", YEAR).values.tolist()


def test_a_branch_named_baseline_gives_way_to_the_arm_in_a_subsample():
    """Core rebuilds the arm from ``branches["baseline"]``. So where the
    caller had named one of a branch's calculation branches "baseline", the
    branch's subsample built its new arm from that one, under the reform:
    with the subsidy repealed, S0 read $0 and the expense $6,000. Now the
    subsample hands core a copy of the arm in its place, and the branch
    reads what a subsample of the reform itself reads. The parent keeps its
    arm, on both households."""
    top = Microsimulation(dataset=new_york_families(), reform=REPEAL)
    top.subsample(n=1, seed=0)
    assert households(top) == [1]
    np.testing.assert_allclose(value(top, SUBSIDY), [0])
    np.testing.assert_allclose(value(top.baseline, SUBSIDY), SAMPLED_S0)
    np.testing.assert_allclose(value(top, EXPENSE), SAMPLED_EXPENSE)

    parent = Microsimulation(dataset=new_york_families(), reform=REPEAL)
    arm = parent.baseline
    trial = parent.get_branch("trial")
    named = trial.get_branch("baseline")
    assert trial.baseline is arm and named is not arm
    trial.subsample(n=1, seed=0)
    own_arm = trial.baseline
    assert own_arm is trial.branches["baseline"]
    assert own_arm is not arm and own_arm is not named
    assert repeals_the_subsidy(trial) and not repeals_the_subsidy(own_arm)
    assert households(trial) == households(own_arm) == [1]
    np.testing.assert_allclose(value(own_arm, SUBSIDY), SAMPLED_S0)
    np.testing.assert_allclose(value(trial, EXPENSE), SAMPLED_EXPENSE)

    assert parent.baseline is arm
    assert households(arm) == [0, 1]


def test_a_failed_branch_subsample_leaves_the_branch_as_it_found_it():
    """Core's subsample raises before it samples anything when given neither
    ``n`` nor ``frac``. The branch then keeps what it held under "baseline":
    nothing, for a branch that shares its parent's arm, or the calculation
    branch the caller named "baseline", the same object. Each branch still
    shares the parent's arm, and a retry reads what a subsample of the
    reform itself reads."""
    parent = Microsimulation(dataset=new_york_families(), reform=REPEAL)
    arm = parent.baseline
    plain = parent.get_branch("plain")
    trial = parent.get_branch("trial")
    named = trial.get_branch("baseline")
    for branch in (plain, trial):
        with pytest.raises(ValueError, match="Either n or frac must be provided"):
            branch.subsample()
        assert branch.baseline is arm
    assert "baseline" not in plain.branches
    assert trial.branches["baseline"] is named

    for branch in (plain, trial):
        branch.subsample(n=1, seed=0)
        assert branch.baseline is not arm
        assert households(branch) == households(branch.baseline) == [1]
        np.testing.assert_allclose(value(branch.baseline, SUBSIDY), SAMPLED_S0)
        np.testing.assert_allclose(value(branch, EXPENSE), SAMPLED_EXPENSE)
    assert parent.baseline is arm
    assert households(arm) == [0, 1]


NAMED_REFUSAL = 'A simulation named "baseline" with a baseline arm cannot subsample'


def test_a_simulation_named_baseline_with_an_arm_refuses_to_subsample():
    """Core rebuilds the arm with ``get_branch("baseline")``, which returns a
    simulation itself when that is its own name. A branch named "baseline"
    under another branch shares the parent's arm, so its subsample put
    baseline policy on the branch and dropped its arm: the repeal read False
    and the expense $14,000 in place of $27,916.40. Now ``subsample`` raises
    before it changes anything, on that branch, a clone of it, a deeper
    branch of that name and a reform simulation renamed "baseline", and each
    keeps its policy, arm, branches and name."""
    parent = Microsimulation(dataset=new_york_families(), reform=REPEAL)
    arm = parent.baseline
    trial = parent.get_branch("trial")
    named = trial.get_branch("baseline")
    renamed = parent.clone()
    renamed.branch_name = "baseline"
    cases = (
        named,
        named.clone(),
        trial.get_branch("deeper").get_branch("baseline"),
        renamed,
    )
    before = [
        (case.baseline, dict(case.branches), case.tax_benefit_system) for case in cases
    ]
    for case, (own_arm, branches, system) in zip(cases, before):
        assert case.branch_name == "baseline" and own_arm is not None
        with pytest.raises(ValueError, match=NAMED_REFUSAL):
            case.subsample(n=1, seed=0)
        assert case.branch_name == "baseline"
        assert case.baseline is own_arm
        assert case.tax_benefit_system is system
        assert case.branches.keys() == branches.keys()
        assert all(case.branches[key] is branches[key] for key in branches)
        assert repeals_the_subsidy(case)
        assert households(case) == [0, 1]
    assert named.baseline is arm
    np.testing.assert_allclose(value(named, SUBSIDY), [0, 0])
    np.testing.assert_allclose(
        value(named, EXPENSE), [27_916.40, 12_000], atol=TOLERANCE
    )
    np.testing.assert_allclose(value(arm, SUBSIDY), [13_916.40, 6_000], atol=TOLERANCE)
    assert trial.branches["baseline"] is named
    assert parent.baseline is arm
    assert households(arm) == [0, 1]


def test_a_failed_subsample_with_no_arm_raises_core_error():
    """A simulation with no reform has no arm and no "baseline" entry, so
    ``subsample`` hands core no copy and has nothing to put back when core
    raises. Core's own ``ValueError`` reaches the caller, rather than a
    ``KeyError`` from removing an entry that was never there, and the
    simulation still has no arm."""
    simulation = Microsimulation(dataset=new_york_families())
    assert simulation.baseline is None
    assert "baseline" not in simulation.branches
    with pytest.raises(ValueError, match="Either n or frac must be provided"):
        simulation.subsample()
    assert "baseline" not in simulation.branches
    assert simulation.baseline is None


# What both New York families reported paying for care, which baseline policy
# keeps over a dataset; under REPEAL, that plus the subsidy lost, S0, which the
# reform reads from its arm.
REPORTED_EXPENSE = [14_000, 6_000]
REPEALED_EXPENSE = [27_916.40, 12_000]
NEW_YORK_S0 = [13_916.40, 6_000]
DATASET_INPUTS = "_dataset_inputs"
PROVENANCE = "_social_security_input_provenance"
BASELINE_ARM_OVERRIDES = "_baseline_arm_overrides"
DUMP_MARK_FILE = "dataset_inputs.json"
NOT_TRUE_OR_FALSE = "the mark must be true or false"


@pytest.fixture(scope="module")
def new_york_source():
    """Both New York families over a dataset, with no reform. The second
    receives a Social Security benefit, so a snapshot carries the provenance
    envelope beside the dataset mark."""
    return Simulation(dataset=dataset((NEW_YORK,), FAMILIES))


def assert_dataset_reading(simulation, households=slice(None)):
    """The expense a dataset simulation computes: the reported amount with no
    reform, and under REPEAL that plus the subsidy lost, read from an arm
    that keeps the reported amount."""
    reported = REPORTED_EXPENSE[households]
    if simulation.baseline is None:
        np.testing.assert_allclose(value(simulation, EXPENSE), reported, atol=TOLERANCE)
        return
    assert repeals_the_subsidy(simulation)
    np.testing.assert_allclose(value(simulation, SUBSIDY), [0] * len(reported))
    np.testing.assert_allclose(
        value(simulation, EXPENSE), REPEALED_EXPENSE[households], atol=TOLERANCE
    )
    arm = simulation.baseline
    assert not repeals_the_subsidy(arm)
    np.testing.assert_allclose(
        value(arm, SUBSIDY), NEW_YORK_S0[households], atol=TOLERANCE
    )
    np.testing.assert_allclose(value(arm, EXPENSE), reported, atol=TOLERANCE)


def test_a_dataset_snapshot_reloads_with_the_dataset_reading(new_york_source):
    """Over a dataset, the pre-subsidy input reads as what parents paid after
    any subsidy; in a household, as the amount before it. A snapshot used to
    reload as a household, so the first family's expense fell from $14,000
    to $83.60. Now the snapshot carries a mark, and the reload, a branch of
    it and a second snapshot of it keep the dataset reading. The branch is
    taken before the reload calculates anything, so it reads the expense
    itself rather than copying the reload's."""
    payload = export_source_inputs(new_york_source)
    assert_dataset_reading(new_york_source)
    reloaded = reload_source_inputs(payload)
    branch = reloaded.get_branch("trial")
    assert not reloaded.is_over_dataset
    assert_dataset_reading(branch)
    np.testing.assert_allclose(
        value(reloaded, EXPENSE), value(new_york_source, EXPENSE), atol=TOLERANCE
    )
    assert_dataset_reading(reloaded)
    again = export_source_inputs(reloaded)
    assert_dataset_reading(reload_source_inputs(again))
    for snapshot in (payload, again):
        assert snapshot["version"] == 1 and snapshot[DATASET_INPUTS] is True
        assert snapshot[PROVENANCE] is not None


def test_a_dataset_snapshot_reloaded_under_a_reform_keeps_the_reading_in_its_arm(
    new_york_source,
):
    """Core builds a reform's arm inside ``__init__``, by cloning the
    simulation, so the mark must be on the simulation before then. The
    reform reads S0 from the arm, and the arm keeps the reported amount."""
    payload = export_source_inputs(new_york_source)
    assert_dataset_reading(reload_source_inputs(payload, reform=REPEAL))


def test_a_reform_over_a_dataset_keeps_the_reading_through_a_snapshot():
    """A source built with the reform exports the mark too, from the reform
    and from its arm, and each reloads with the dataset reading."""
    source = Simulation(dataset=dataset((NEW_YORK,), FAMILIES), reform=REPEAL)
    assert_dataset_reading(source)
    payload = export_source_inputs(source)
    assert payload[DATASET_INPUTS] is True
    assert_dataset_reading(reload_source_inputs(payload, reform=REPEAL))
    arm_payload = export_source_inputs(source.baseline)
    assert arm_payload[DATASET_INPUTS] is True
    assert_dataset_reading(reload_source_inputs(arm_payload))


def test_a_person_extracted_from_a_dataset_keeps_the_reading(new_york_source):
    """``extract_person`` marks the situation it extracts from a dataset
    simulation, and a simulation built from it, with or without a reform,
    reads the expense as the dataset does."""
    for person, households in ((0, slice(0, 1)), (2, slice(1, 2))):
        extracted = json.loads(json.dumps(new_york_source.extract_person(person)))
        built = Simulation(situation=extracted)
        assert not built.is_over_dataset
        assert_dataset_reading(built, households)
        assert_dataset_reading(
            Simulation(situation=extracted, reform=REPEAL), households
        )
        assert extracted[DATASET_INPUTS] is True


def test_an_unmarked_snapshot_reloads_as_a_household(new_york_source):
    """A version 1 snapshot without the mark, as export wrote before it
    recorded one, reloads as a household: each family's expense nets its
    subsidy, $14,000 less $13,916.40 and $6,000 less $6,000. A snapshot of
    that reload carries no mark either."""
    payload = export_source_inputs(new_york_source)
    del payload[DATASET_INPUTS]
    reloaded = reload_source_inputs(payload)
    np.testing.assert_allclose(value(reloaded, EXPENSE), [83.60, 0], atol=TOLERANCE)
    assert DATASET_INPUTS not in export_source_inputs(reloaded)


def test_a_mark_other_than_true_or_false_raises(new_york_source):
    """The builder and the reload take the mark as true or false. JSON false
    reads as no mark, so the first family's expense nets its subsidy, and
    any other value raises before anything is built."""
    extracted = json.loads(json.dumps(new_york_source.extract_person(0)))
    payload = export_source_inputs(new_york_source)
    for mark in ("true", 1):
        with pytest.raises(ValueError, match=NOT_TRUE_OR_FALSE):
            Simulation(situation={**extracted, DATASET_INPUTS: mark})
        with pytest.raises(ValueError, match=NOT_TRUE_OR_FALSE):
            reload_source_inputs({**payload, DATASET_INPUTS: mark})
    unmarked = (
        Simulation(
            situation=json.loads(json.dumps({**extracted, DATASET_INPUTS: False}))
        ),
        reload_source_inputs(
            json.loads(json.dumps({**payload, DATASET_INPUTS: False}))
        ),
    )
    for simulation in unmarked:
        np.testing.assert_allclose(value(simulation, EXPENSE)[0], 83.60, atol=TOLERANCE)


# The dataset counts $40,000 of the first New York family's income for its
# child care program, where the program's formula counts $30,000, so baseline
# policy pays that family $100 less, and gives it $2,000 of other work
# expenses, W, where the formula gives none.
GIVEN = {"ny_ccap_countable_income": (40_000, 0), "spm_unit_work_expenses": (2_000, 0)}
GIVEN_S0 = [13_816.40, 6_000]
GIVEN_ARM_EXPENSE = [16_000, 6_000]
GIVEN_EXPENSE = [29_816.40, 12_000]


def given_source():
    return Simulation(
        dataset=dataset((NEW_YORK,), FAMILIES, given=GIVEN), reform=REPEAL
    )


@pytest.fixture(scope="module")
def given_snapshot():
    """``given_source`` and its snapshot, which the tests below only read."""
    source = given_source()
    return source, export_source_inputs(source)


def test_a_marked_reload_sets_the_snapshots_overrides_on_its_arm(given_snapshot):
    """Over a dataset, core gives the reform and its arm each value the
    dataset gives. Export lists a value given for a variable with a formula,
    such as New York's countable income, among the overrides, and the reload
    set those on the reform side only. Its arm then calculated S0 at
    $13,916.40 where the source's arm reads $13,816.40, and the reform's
    expense read $100 more than the source's. Now a marked reload sets each
    override on its arm too."""
    source, payload = given_snapshot
    assert GIVEN.keys() <= payload["overrides"].keys()
    assert BASELINE_ARM_OVERRIDES not in payload
    reloaded = reload_source_inputs(payload, reform=REPEAL)
    np.testing.assert_allclose(
        value(reloaded, EXPENSE), value(source, EXPENSE), atol=TOLERANCE
    )
    np.testing.assert_allclose(value(source, EXPENSE), GIVEN_EXPENSE, atol=TOLERANCE)
    arm = reloaded.baseline
    for name in (SUBSIDY, EXPENSE, "ny_ccap_countable_income"):
        np.testing.assert_allclose(
            value(arm, name), value(source.baseline, name), atol=TOLERANCE
        )
    np.testing.assert_allclose(value(arm, SUBSIDY), GIVEN_S0, atol=TOLERANCE)


def test_a_marked_reload_arm_keeps_the_datasets_work_expense(given_snapshot):
    """The source's arm holds the $2,000 of work expenses the dataset gives,
    so it reads $16,000 for the first family's expense. The reload's arm
    calculated W at $0 and read $14,000."""
    source, payload = given_snapshot
    arm = reload_source_inputs(payload, reform=REPEAL).baseline
    np.testing.assert_allclose(value(arm, "spm_unit_work_expenses"), [2_000, 0])
    for simulation in (arm, source.baseline):
        np.testing.assert_allclose(
            value(simulation, EXPENSE), GIVEN_ARM_EXPENSE, atol=TOLERANCE
        )


def test_an_unmarked_reload_sets_overrides_on_the_reform_side_only(given_snapshot):
    """Without the mark, the reload sets the overrides on the reform side
    alone, as on main, and its arm calculates both variables."""
    _, payload = given_snapshot
    unmarked = {key: item for key, item in payload.items() if key != DATASET_INPUTS}
    reloaded = reload_source_inputs(unmarked, reform=REPEAL)
    np.testing.assert_allclose(value(reloaded, "ny_ccap_countable_income"), [40_000, 0])
    np.testing.assert_allclose(value(reloaded, "spm_unit_work_expenses"), [2_000, 0])
    arm = reloaded.baseline
    np.testing.assert_allclose(value(arm, "ny_ccap_countable_income"), [30_000, 19_200])
    np.testing.assert_allclose(value(arm, "spm_unit_work_expenses"), [0, 0])


def test_a_marked_reload_keeps_values_set_on_the_reform_side_off_its_arm():
    """A caller who sets a value on the reform after construction sets it
    there alone. The source's arm keeps the $2,000 of work expenses the
    dataset gave under the $3,000 set, and calculates the earned cap set to
    $20,000. Export lists what the arm holds for each override it doesn't
    share, null where it holds nothing, and the reload's arm takes that, so
    both sides match the source's, through a second snapshot too."""
    source = given_source()
    source.set_input("spm_unit_work_expenses", YEAR, [3_000, 0])
    source.set_input("spm_unit_head_spouse_earned_cap", YEAR, [20_000, 20_000])
    payload = export_source_inputs(source)
    reloaded = reload_source_inputs(payload, reform=REPEAL)
    names = ("spm_unit_work_expenses", "spm_unit_head_spouse_earned_cap", EXPENSE)
    for name in names:
        for side, source_side in (
            (reloaded, source),
            (reloaded.baseline, source.baseline),
        ):
            np.testing.assert_allclose(
                value(side, name), value(source_side, name), atol=TOLERANCE
            )
    np.testing.assert_allclose(
        value(reloaded.baseline, "spm_unit_head_spouse_earned_cap"), [30_000, 18_000]
    )
    assert payload[BASELINE_ARM_OVERRIDES] == {
        "spm_unit_work_expenses": {str(YEAR): [2_000, 0]},
        "spm_unit_head_spouse_earned_cap": {str(YEAR): None},
    }
    again = export_source_inputs(reloaded)
    assert again[BASELINE_ARM_OVERRIDES] == payload[BASELINE_ARM_OVERRIDES]


def test_a_marked_reload_refuses_an_override_the_reform_stores_for_all_time():
    """A dataset with no reform gives New York's first family a $500 subsidy
    for 2026, and export lists it among the overrides. Under a reform that
    stores the subsidy for all time, baseline policy's yearly variable can't
    use the reform's holder, so a reform built over that dataset refuses the
    input. A marked reload refuses it the same way, by name, before it sets
    anything on its arm. An unmarked reload builds, as on main, and its arm
    calculates the subsidy."""
    source = Simulation(
        dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies={YEAR: [500]})
    )
    payload = export_source_inputs(source)
    assert SUBSIDY in payload["overrides"]
    with pytest.raises(ValueError, match=REFUSAL) as refused:
        reload_source_inputs(payload, reform=StoreSubsidiesForAllTime)
    names = [entry.name for entry in refused.traceback]
    assert "_set_overrides_on_the_arm" in names
    assert "_rebuild_baseline_branch" not in names
    unmarked = {key: item for key, item in payload.items() if key != DATASET_INPUTS}
    reloaded = reload_source_inputs(unmarked, reform=StoreSubsidiesForAllTime)
    np.testing.assert_allclose(value(reloaded, SUBSIDY), [500])
    np.testing.assert_allclose(
        value(reloaded.baseline, SUBSIDY), NEW_YORK_S0[:1], atol=TOLERANCE
    )


class spm_unit_reform_only_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "An amount only the reform defines"
    definition_period = "year"

    def formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_pre_subsidy_childcare_expenses", period) * 0


class AddAVariable(Reform):
    def apply(self):
        self.update_variable(spm_unit_reform_only_amount)


def test_a_marked_reload_skips_an_override_baseline_policy_does_not_define():
    """A dataset under a reform that adds a variable gives it a value, which
    export lists among the overrides. Baseline policy has no such variable,
    so the source's arm has none, and a marked reload sets it on the reform
    side alone and raises nothing."""
    name = "spm_unit_reform_only_amount"
    source = Simulation(
        dataset=dataset((NEW_YORK,), FAMILIES, given={name: (250, 0)}),
        reform=AddAVariable,
    )
    payload = export_source_inputs(source)
    assert name in payload["overrides"] and BASELINE_ARM_OVERRIDES not in payload
    reloaded = reload_source_inputs(payload, reform=AddAVariable)
    np.testing.assert_allclose(value(reloaded, name), [250, 0])
    assert name not in reloaded.baseline.tax_benefit_system.variables
    assert name not in reloaded.baseline.populations["spm_unit"]._holders
    np.testing.assert_allclose(
        value(reloaded.baseline, EXPENSE), REPORTED_EXPENSE, atol=TOLERANCE
    )


def test_a_dump_of_a_dataset_simulation_restores_with_the_dataset_reading(tmp_path):
    """Core's ``restore_simulation`` builds a plain core simulation, which read
    the pre-subsidy input as a household's: the first family's expense fell
    from $14,000 to $83.60. Now the dump holds the mark in ``__entities__``,
    and the restore sets it, so the restored simulation reads the expense,
    and the second family's Social Security benefit, as its source does. A
    dump without the mark file, as earlier dumps are, restores as a
    household, a mark other than true or false raises, and a household
    simulation's dump holds no mark."""
    source = Simulation(dataset=dataset((NEW_YORK,), FAMILIES))
    directory = tmp_path / "dataset"
    simulation_dumper.dump_simulation(source, str(directory))
    system = source.tax_benefit_system
    restored = simulation_dumper.restore_simulation(str(directory), system)
    np.testing.assert_allclose(
        value(restored, EXPENSE), REPORTED_EXPENSE, atol=TOLERANCE
    )
    np.testing.assert_allclose(value(restored, "social_security"), [0, 0, 1_200, 0])
    np.testing.assert_allclose(
        value(source, "social_security"), value(restored, "social_security")
    )
    mark = directory / "__entities__" / DUMP_MARK_FILE
    assert json.loads(mark.read_text()) is True
    mark.unlink()
    unmarked = simulation_dumper.restore_simulation(str(directory), system)
    np.testing.assert_allclose(value(unmarked, EXPENSE), [83.60, 0], atol=TOLERANCE)
    mark.write_text("1")
    with pytest.raises(ValueError, match=NOT_TRUE_OR_FALSE):
        simulation_dumper.restore_simulation(str(directory), system)
    household = tmp_path / "household"
    simulation_dumper.dump_simulation(Simulation(situation=situation()), str(household))
    assert not (household / "__entities__" / DUMP_MARK_FILE).exists()
