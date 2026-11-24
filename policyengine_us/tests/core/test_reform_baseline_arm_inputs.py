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
the reform still holds for a variable it stores apart from baseline policy,
wherever the baseline's definition can hold that input. Without that step, a
yearly subsidy the reform stores for all time left the arm calculating one.

Invariants: under a reform that changes nothing, the reform and its baseline
arm compute what a simulation with no reform computes, for every household,
whether a situation or a dataset of raw columns supplies the inputs. Under any
reform, each holder in either arm suits that arm's definition of its variable.
Under a reform that stores a variable apart from baseline policy, other than an
entity ID, membership ID or role, the arm sets again the last array the reform
stored for each period it still holds, in the order those periods were last
set, through deletions and subsamples, and reads them as a simulation with no
reform given them in that order reads them. Subsampling leaves the reform's
own value, and the households it samples, as they were. A deletion on a holder for all time
deletes every year's input, so the reform then holds none. Where the reform's
holder took an input its ``set_input`` never saw, such as a write to the
holder itself, the arm calculates what it can't place: under a reform for all
time, each year given no input since; under a yearly reform, the variable.

Three cases fall outside these invariants, and no test pins them. A write the
record never saw that stores the very array it kept last under that key goes
unnoticed, so the arm sets what was kept, in the order kept. Under a yearly
reform of a variable baseline policy stores for all time, deleting one year's
input leaves the reform its other years, which the arm sets again, while a
simulation with no reform loses every year's input. And core's handlers divide
or dispatch an input over several periods around the inputs a holder already
has, so the arrays the reform stored, and the last of them for each period,
can tell another story than the inputs first given: where such inputs overlap,
or the reform's handler stored one around an earlier input, the arm can read
other values than a simulation with no reform given those inputs.
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
from policyengine_us.entities import Household, Person, SPMUnit
from policyengine_us.variables.gov.hhs.ccdf.child_care_subsidies import (
    child_care_subsidies as yearly_child_care_subsidies,
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


SUBSIDY = "child_care_subsidies"
TWO_YEARS = {2025: [400, 600], YEAR: [500, 700]}


def delete_then_set(simulation):
    simulation.delete_arrays(SUBSIDY)
    simulation.set_input(SUBSIDY, YEAR, [800, 900])


def delete_on_the_holder_then_set(simulation):
    # PolicyEngine's input moves delete on the holder, not the simulation.
    simulation.get_holder(SUBSIDY).delete_arrays()
    simulation.set_input(SUBSIDY, YEAR, [800, 900])


def set_the_first_year_again(simulation):
    simulation.set_input(SUBSIDY, 2025, [450, 650])


@pytest.mark.parametrize(
    "change",
    [
        None,
        delete_then_set,
        delete_on_the_holder_then_set,
        set_the_first_year_again,
    ],
)
def test_subsampling_gives_the_arm_each_yearly_subsidy_the_reform_holds(change):
    """Core subsamples by rebuilding the simulation from what its holders
    record, and the reform's holder for all time records neither year. Both
    runs read the same dataset and receive the same inputs and deletions, and
    the sample keeps only the second household. The arm then reads each
    year's subsidy as the simulation with no reform does, and the reform keeps
    the subsidy it held. Before, a deleted input came back. A subsample that
    fails before core rebuilds anything keeps the inputs in place."""
    simulations = [
        Microsimulation(
            dataset=dataset(
                (NEW_YORK,), FAMILIES, yearly_subsidies=TWO_YEARS, weights=(0, 1)
            ),
            reform=reform,
        )
        for reform in (None, StoreSubsidiesForAllTime)
    ]
    plain, reformed = simulations
    for simulation in simulations:
        if change is not None:
            change(simulation)
    held = value(reformed, SUBSIDY)[1]
    with pytest.raises(ValueError, match="Either n or frac"):
        reformed.subsample()
    for simulation in simulations:
        simulation.subsample(n=1)
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
        assert simulation.calculate("household_id", YEAR).values.tolist() == [1]
    for year in TWO_YEARS:
        np.testing.assert_allclose(
            value(arm, SUBSIDY, year), value(plain, SUBSIDY, year), atol=TOLERANCE
        )
        np.testing.assert_allclose(value(reformed, SUBSIDY, year), [held])
    expense = "spm_unit_capped_work_childcare_expenses"
    np.testing.assert_allclose(
        value(arm, expense), value(plain, expense), atol=TOLERANCE
    )


def test_the_arm_sets_a_numeric_expression_as_core_stored_it():
    """Core evaluates a numeric expression it is given for a numeric variable
    and stores the result, $600. The arm sets that 2026 subsidy after a
    subsample, beside the dataset's $400 for 2025. Before, the arm received
    the expression as an array of text, and setting it raised a
    ValueError."""
    subsidies = {2025: [400], YEAR: [500]}
    simulations = [
        Microsimulation(
            dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies=subsidies),
            reform=reform,
        )
        for reform in (None, StoreSubsidiesForAllTime)
    ]
    for simulation in simulations:
        simulation.set_input(SUBSIDY, YEAR, "400 + 200")
        simulation.subsample(n=1)
    plain, reformed = simulations
    arm = reformed.baseline
    for year, subsidy in ((2025, 400), (YEAR, 600)):
        np.testing.assert_allclose(value(plain, SUBSIDY, year), [subsidy])
        np.testing.assert_allclose(value(arm, SUBSIDY, year), [subsidy])
        np.testing.assert_allclose(value(reformed, SUBSIDY, year), [600])


class RestoreYearlySubsidies(Reform):
    def apply(self):
        self.update_variable(yearly_child_care_subsidies)


def test_a_reform_that_restores_the_yearly_subsidy_leaves_none_to_set_again():
    """Applying a reform that restores baseline policy's yearly subsidy drops
    the holder that stored it for all time, with its input, so the reform
    calculates the subsidy. A later subsample then gives the arm no input the
    reform no longer holds, and the two read the same subsidy each year."""
    reformed = Microsimulation(
        dataset=dataset(
            (NEW_YORK,), FAMILIES, yearly_subsidies=TWO_YEARS, weights=(0, 1)
        ),
        reform=StoreSubsidiesForAllTime,
    )
    reformed.apply_reform(RestoreYearlySubsidies)
    reformed.subsample(n=1)
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
    for year in TWO_YEARS:
        np.testing.assert_allclose(
            value(arm, SUBSIDY, year), value(reformed, SUBSIDY, year), atol=TOLERANCE
        )
    expense = "spm_unit_capped_work_childcare_expenses"
    np.testing.assert_allclose(
        value(reformed, expense), value(arm, expense), atol=TOLERANCE
    )


class household_weight(Variable):
    # Stored for all time, where baseline policy stores a weight each year.
    value_type = float
    entity = Household
    label = "Household weight"
    definition_period = ETERNITY


class StoreWeightsForAllTime(Reform):
    def apply(self):
        self.update_variable(household_weight)


@pytest.mark.parametrize("period", [None, "month:2025-01:12", "month:2026-02:12"])
def test_subsampling_reweights_a_weight_the_reform_stores_for_all_time(period):
    """Two households weigh 1 each, and a sample of one keeps their total of
    2. The arm reads the sampled household's yearly weight as the simulation
    with no reform does. Before, the arm set the weight the dataset gave, 1.

    A weight given for twelve months reaches the arm as a column named for
    its period, which core parses back to reweight it. Twelve months from
    January parse back as the year, and from February as a year from
    February, so neither equals the period kept; matching on the period
    raised ``TypeError`` from the subsample."""
    simulations = [
        Microsimulation(dataset=dataset((NEW_YORK,), FAMILIES), reform=reform)
        for reform in (None, StoreWeightsForAllTime)
    ]
    for simulation in simulations:
        if period is not None:
            simulation.set_input("household_weight", period, [1.0, 1.0])
        simulation.subsample(n=1, seed=0)
    plain, reformed = simulations
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
    for simulation in (reformed, arm):
        assert (
            simulation.calculate("household_id", YEAR).values.tolist()
            == plain.calculate("household_id", YEAR).values.tolist()
        )
    weight = np.asarray(plain.calculate("household_weight", YEAR, use_weights=False))
    np.testing.assert_allclose(weight, [2])
    for simulation in (reformed, arm):
        np.testing.assert_allclose(
            simulation.calculate("household_weight", YEAR, use_weights=False), weight
        )


class household_id(Variable):
    # Stored for all time, where baseline policy stores an ID each year.
    value_type = int
    entity = Household
    label = "Unique reference for this household"
    definition_period = ETERNITY


class person_household_id(Variable):
    value_type = int
    entity = Person
    label = "Unique reference for the household of this person"
    definition_period = ETERNITY


class StoreHouseholdIdsForAllTime(Reform):
    def apply(self):
        self.update_variable(household_id)
        self.update_variable(person_household_id)


def test_subsampling_selects_households_by_the_reforms_own_ids():
    """The reform gives the two households each other's ID for the year
    before, which it holds for all time, and a sample of one picks the family
    that a simulation with no reform, given those IDs for this year, picks.
    Core selects households by the first household ID column of its export,
    so the arm sets again no entity ID, membership ID or role. Before, the
    arm kept the dataset's IDs, their column came first, and the reform
    sampled the other family."""
    simulations = [
        Microsimulation(dataset=dataset((NEW_YORK,), FAMILIES), reform=reform)
        for reform in (None, StoreHouseholdIdsForAllTime)
    ]
    plain, reformed = simulations
    plain.set_input("household_id", YEAR, [1, 0])
    reformed.set_input("household_id", YEAR - 1, [1, 0])
    for simulation in simulations:
        simulation.subsample(n=1, seed=0)
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
    income = value(plain, "employment_income_before_lsr")
    assert income.tolist() in ([30_000, 0], [15_000, 0])
    for simulation in (reformed, arm):
        np.testing.assert_allclose(
            value(simulation, "employment_income_before_lsr"), income
        )


def write_on_the_holder(simulation):
    simulation.get_holder(SUBSIDY).set_input(YEAR, np.array([800.0, 900.0]))


def edit_the_stored_array(simulation):
    simulation.get_holder(SUBSIDY).get_array(YEAR)[:] = [800.0, 900.0]


@pytest.mark.parametrize(
    "write, held",
    [
        (write_on_the_holder, 900),
        (edit_the_stored_array, 900),
    ],
)
def test_the_arm_sets_none_of_the_inputs_a_write_to_the_holder_replaced(write, held):
    """A write to the reform's holder itself, as core's situation builder
    makes, or an edit in place to the array it stores, replaces the subsidy
    kept for all time without telling the record. The arm then sets none of
    the kept yearly inputs and calculates both years, as a simulation with no
    subsidy input does, rather than the replaced $600 and $700."""
    simulations = [
        Microsimulation(
            dataset=dataset(
                (NEW_YORK,), FAMILIES, yearly_subsidies=TWO_YEARS, weights=(0, 1)
            ),
            reform=reform,
        )
        for reform in (None, StoreSubsidiesForAllTime)
    ]
    plain, reformed = simulations
    plain.delete_arrays(SUBSIDY)
    write(reformed)
    for simulation in simulations:
        simulation.subsample(n=1)
    arm = reformed.baseline
    for year in TWO_YEARS:
        calculated = value(plain, SUBSIDY, year)
        assert calculated[0] not in TWO_YEARS[year]
        np.testing.assert_allclose(
            value(arm, SUBSIDY, year), calculated, atol=TOLERANCE
        )
        np.testing.assert_allclose(value(reformed, SUBSIDY, year), [held])


class is_household_head(Variable):
    # Stored each year, where baseline policy stores it for all time.
    value_type = bool
    entity = Person
    label = "is head of this household"
    definition_period = "year"


class StoreHeadsEachYear(Reform):
    def apply(self):
        self.update_variable(is_household_head)


@pytest.mark.parametrize("period", [2025, "month:2025-01:12", "month:2025-01:24"])
def test_subsampling_keeps_the_order_of_inputs_baseline_policy_stores_for_all_time(
    period,
):
    """The dataset names each household's parent its head in 2026, and both
    runs then name each child head in 2025. Baseline policy stores the role
    for all time, so the input set last wins. The reform stores it each year,
    and core exports its years in order, 2025 first; the arm sets them in the
    order the reform received them, so it reads the child as head, as the
    simulation with no reform does. Core stores twelve months from January
    as the year, and so does the record. Over 24 months, the reform's holder
    stores the input for 2025 alone, since 2026 already holds one, and the
    record keeps what it stored."""
    simulations = [
        Microsimulation(
            dataset=dataset((NEW_YORK,), FAMILIES, weights=(0, 1)), reform=reform
        )
        for reform in (None, StoreHeadsEachYear)
    ]
    for simulation in simulations:
        simulation.set_input("is_household_head", period, [False, True, False, True])
    for simulation in simulations:
        simulation.subsample(n=1)
    plain, reformed = simulations
    arm = reformed.baseline
    for simulation in (reformed, arm):
        assert_holders_suit_their_variables(simulation)
    heads = plain.calculate("is_household_head", YEAR, use_weights=False)
    assert np.asarray(heads).tolist() == [False, True]
    assert np.asarray(
        arm.calculate("is_household_head", YEAR, use_weights=False)
    ).tolist() == [False, True]
    assert np.asarray(
        reformed.calculate("is_household_head", YEAR, use_weights=False)
    ).tolist() == [True, False]


def test_after_a_write_to_the_holder_the_arm_sets_only_the_inputs_given_since():
    """A write to the reform's holder itself stores $900 for all time where the
    record kept the dataset's $700, and both runs then set $650 for 2025. The
    record can't tell which year the write was for, so it starts again from
    the 2025 input: the arm sets it and calculates 2026, as a simulation with
    no reform does once its 2026 input is gone. Before, the record took the
    2025 input as following the kept ones, and the arm set the replaced $700
    for 2026."""
    simulations = [
        Microsimulation(
            dataset=dataset(
                (NEW_YORK,), FAMILIES, yearly_subsidies=TWO_YEARS, weights=(0, 1)
            ),
            reform=reform,
        )
        for reform in (None, StoreSubsidiesForAllTime)
    ]
    for simulation in simulations:
        simulation.get_holder(SUBSIDY).set_input(YEAR, np.array([800.0, 900.0]))
        simulation.set_input(SUBSIDY, 2025, [450, 650])
        simulation.subsample(n=1)
    plain, reformed = simulations
    arm = reformed.baseline
    for simulation in (plain, arm):
        np.testing.assert_allclose(value(simulation, SUBSIDY, 2025), [650])
    np.testing.assert_allclose(value(plain, SUBSIDY, YEAR), [900])
    np.testing.assert_allclose(value(reformed, SUBSIDY, YEAR), [650])
    plain.delete_arrays(SUBSIDY, YEAR)
    calculated = value(plain, SUBSIDY, YEAR)
    assert calculated[0] not in (700, 900)
    np.testing.assert_allclose(value(arm, SUBSIDY, YEAR), calculated, atol=TOLERANCE)


# Stored for all time, and defined only through 2025. Core names a variable
# after its class.
subsidies_for_all_time_until_2025 = type(
    "child_care_subsidies",
    (Variable,),
    dict(
        value_type=float,
        entity=SPMUnit,
        label="Child care subsidies",
        definition_period=ETERNITY,
        end="2025-12-31",
    ),
)


class StoreSubsidiesForAllTimeUntil2025(Reform):
    def apply(self):
        self.update_variable(subsidies_for_all_time_until_2025)


def test_the_arm_sets_no_input_the_reform_did_not_store():
    """The reform's subsidy ends with 2025, so core stores the dataset's 2026
    subsidy nowhere. The arm sets the $400 for 2025 and calculates 2026, as a
    simulation with no reform does without a 2026 input. Before, the record
    kept what the holder stored, the 2025 subsidy, for 2026 as well, and the
    arm set $400 there."""
    subsidies = {2025: [400], YEAR: [500]}
    plain, reformed = [
        Microsimulation(
            dataset=dataset((NEW_YORK,), FAMILIES[:1], yearly_subsidies=subsidies),
            reform=reform,
        )
        for reform in (None, StoreSubsidiesForAllTimeUntil2025)
    ]
    arm = reformed.baseline
    np.testing.assert_allclose(value(arm, SUBSIDY, 2025), [400])
    plain.delete_arrays(SUBSIDY, YEAR)
    calculated = value(plain, SUBSIDY, YEAR)
    assert calculated[0] not in (400, 500)
    np.testing.assert_allclose(value(arm, SUBSIDY, YEAR), calculated, atol=TOLERANCE)


HEAD = "is_household_head"


def heads(simulation, year=YEAR):
    return np.asarray(simulation.calculate(HEAD, year, use_weights=False)).tolist()


def test_the_arm_calculates_a_role_written_to_the_reform_holder():
    """Under the yearly reform, a write to the holder itself names the child
    head in 2027, and both runs then name the parent head in 2025. The record
    never saw the 2027 input, and baseline policy keeps only the role set
    last, so the arm can't tell which input it would end with. It calculates
    the role, through two subsamples, as a simulation with no reform does
    with no role input. Before, the first subsample exported the 2027 input
    after the kept ones, and the arm named the child head."""
    simulations = [
        Microsimulation(dataset=dataset((NEW_YORK,), FAMILIES[:1]), reform=reform)
        for reform in (None, StoreHeadsEachYear)
    ]
    for simulation in simulations:
        simulation.get_holder(HEAD).set_input(2027, np.array([False, True]))
        simulation.set_input(HEAD, 2025, [True, False])
    plain, reformed = simulations
    for _ in range(2):
        for simulation in simulations:
            simulation.subsample(n=1)
        arm = reformed.baseline
        assert_holders_suit_their_variables(arm)
        assert heads(plain) == [True, False]
        assert heads(arm) == [False, False]
        assert heads(reformed, 2025) == [True, False]
        assert heads(reformed, 2027) == [False, True]
    plain.delete_arrays(HEAD)
    assert heads(plain) == heads(arm)


def test_a_failed_subsample_leaves_no_export_behind():
    """Under the yearly reform, both runs name each child head in 2025, a
    subsample fails before core rebuilds anything, and both then name each
    parent head in 2025. A sample then reads the parent as head in the arm
    and in 2025's reform, as in the simulation with no reform. Had the failed
    subsample left its export in place, the reform would have kept the
    child's 2025 role from it."""
    simulations = [
        Microsimulation(
            dataset=dataset((NEW_YORK,), FAMILIES, weights=(0, 1)), reform=reform
        )
        for reform in (None, StoreHeadsEachYear)
    ]
    for simulation in simulations:
        simulation.set_input(HEAD, 2025, [False, True, False, True])
    plain, reformed = simulations
    with pytest.raises(ValueError, match="Either n or frac"):
        reformed.subsample()
    for simulation in simulations:
        simulation.set_input(HEAD, 2025, [True, False, True, False])
        simulation.subsample(n=1)
    arm = reformed.baseline
    assert heads(plain) == [True, False]
    assert heads(arm) == [True, False]
    assert heads(reformed, 2025) == [True, False]
