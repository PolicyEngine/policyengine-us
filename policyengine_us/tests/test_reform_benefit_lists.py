"""Reforms that pay a benefit add it to the baseline benefit lists.

The Texas rebate, the End Child Poverty Act, its Economic Dignity for All
Agenda version and the BOOST Act credit each pay a benefit, and each replaced
spm_unit_benefits with its own copy of the program list. The copies fell behind
the baseline, and every program a copy missed dropped out of SPM resources for
every household the reform applied to (#10226):

- Texas missed 19 state SSI supplements, and the three Tlaib copies missed 42
  supplements, Washington's cash programs (wa_sfa, wa_rca) and the Washington
  and West Virginia child care subsidies.
- The Tlaib copies listed acp and ebb, which spm_unit_net_income also adds, so
  ACP and EBB counted twice in SPM resources.
- The ECPA and BOOST copies of household_benefits missed CSFP and
  household_health_benefits.

Each reform now adds its own variables to the gov.household lists that the
baseline aggregates read, through add_to_list_parameter. These invariants hold
for every input:

1. add_to_list_parameter keeps every dated value of a list and its members in
   order, appends only the names a value lacks, and changes nothing when it
   runs again. It writes new lists, leaving the names it gets and the member
   lists it reads unchanged, and it changes values only through
   Parameter.update, so the parent node returns the new lists. Every call
   marks the parameter and its parent modified, even a call that adds nothing.
2. Under each reform, every list parameter in the model holds, on every day,
   the baseline list followed by the reform's own additions and nothing else.
   That covers the household and SPM benefit lists, the lists their members
   sum (household_state_benefits, state_property_tax_refunds,
   child_care_subsidy_programs and the rest) and every other list. A reformed
   system marks modified exactly the lists its reform changes, and current law
   marks none.
3. Applying a reform a second time changes no list. A simulation can apply a
   structural reform twice: once when its system is built, once at start.
4. No reform neutralizes a benefit total or changes its formula. The totals
   are household_benefits, spm_unit_benefits and every variable that sums a
   list feeding them, at any depth; this file derives them from the built model
   and checks that test_aggregate_list_integrity.py, which scans the source,
   finds the same ones. A total that a reform zeroed would drop out of both
   sides of the sums in 5, so 5 alone would not catch it.
5. For any household, spm_unit_benefits and household_benefits equal the sum
   of the baseline list's programs and the reform's own additions, each as the
   simulation computes it; spm_unit_benefits also adds the SPM's capped housing
   subsidy. A program that a copy drops, or that it counts twice, breaks the
   sum.
6. A dollar of ACP or EBB adds a dollar to spm_unit_net_income, under current
   law and under each reform.
"""

import gc
import importlib.util
from datetime import date, timedelta
from pathlib import Path

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.periods import instant

from policyengine_us import Simulation
from policyengine_us.reforms.congress.tlaib.boost.boost_middle_class_tax_credit import (
    boost_middle_class_tax_credit,
)
from policyengine_us.reforms.congress.tlaib.economic_dignity_for_all_agenda.edaa_end_child_poverty_act import (
    end_child_poverty_act as edaa_end_child_poverty_act,
)
from policyengine_us.reforms.congress.tlaib.end_child_poverty_act import (
    end_child_poverty_act,
)
from policyengine_us.reforms.states.tx.rebate.tx_rebate import tx_rebate
from policyengine_us.system import CountryTaxBenefitSystem, system
from policyengine_us.tools.parameters import add_to_list_parameter

STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()

SPM = "gov.household.spm_unit_benefits"
HOUSEHOLD = "gov.household.household_benefits"
STATE = "gov.household.household_state_benefits"

# The structural reforms that name a benefit total or list, and the variable
# each adds to the household and SPM benefit lists. A reform that only reads a
# total belongs here too, with None in place of a variable.
# test_aggregate_list_integrity.py fails when a reform names one and is missing
# from this dict.
REFORMS = {
    "tx_rebate": (tx_rebate, "tx_rebate"),
    "end_child_poverty_act": (end_child_poverty_act, "ecpa_child_benefit"),
    "edaa_end_child_poverty_act": (edaa_end_child_poverty_act, "ecpa_child_benefit"),
    "boost_middle_class_tax_credit": (
        boost_middle_class_tax_credit,
        "boost_middle_class_tax_credit_paid_through_ssa",
    ),
}
OWN_BENEFITS = sorted({benefit for _, benefit in REFORMS.values() if benefit})

# What the spm_unit_benefits formula adds to its parameter list under current
# law. The housing subsidy stays out of the parameter so that no other
# aggregate reads an SPM valuation cap.
SPM_FORMULA_BENEFITS = ["spm_unit_capped_housing_subsidy"]


# additions() changes only on January 1 of these years.
ADDITION_YEARS = range(2000, 2051)


def additions(name, parameter, year):
    """The variables a reform adds to a list parameter in a year."""
    if name == "baseline" or REFORMS[name][1] is None:
        return []
    own = REFORMS[name][1]
    if name == "tx_rebate":
        # A state benefit: household_benefits reads it through
        # household_state_benefits, which carries it in 2027, its paid year.
        if parameter == SPM or (parameter == STATE and year == 2027):
            return [own]
        return []
    return [own] if parameter in (SPM, HOUSEHOLD) else []


def changes(name, parameter):
    """True when a reform adds to a list parameter in any year."""
    return any(additions(name, parameter, year) for year in ADDITION_YEARS)


def benefit_list(tax_benefit_system, parameter, year):
    """A benefit list as formulas read it in a year.

    Reading the one parameter, not parameters(year), keeps the test from
    building and caching the whole parameter tree for every year it draws.
    """
    return list(tax_benefit_system.parameters.get_child(parameter)(f"{year}-01-01"))


def list_parameters(tax_benefit_system):
    """{name: parameter} for every parameter in the model whose values are lists."""
    return {
        parameter.name: parameter
        for parameter in tax_benefit_system.parameters.get_descendants()
        if isinstance(parameter, Parameter)
        and any(isinstance(value.value, list) for value in parameter.values_list)
    }


def dated(parameter):
    """A parameter's dated values, as (first day, value) pairs."""
    return [(value.instant_str, value.value) for value in parameter.values_list]


def members_on(parameter, day):
    """The members a list parameter holds on a day, or None in a gap."""
    value = parameter(day)
    return None if value is None else list(value)


def breakpoints(*parameters):
    """The days on which these lists, or a reform's additions, can change.

    Lists that agree on each of these days agree on every day from the year
    1000 on: a list changes only on the first day of one of its values, and
    additions() only on January 1 of a year in ADDITION_YEARS.
    """
    starts = {
        value.instant_str
        for parameter in parameters
        for value in parameter.values_list
        if value.instant_str >= "1000"
    }
    years = {f"{year}-01-01" for year in ADDITION_YEARS}
    return sorted(starts | years | {"1000-01-01"})


BASELINE_LISTS = list_parameters(system)

# The integrity test reads the source and never builds the model; load it by
# path to compare its benefit totals with the ones the built model gives.
_spec = importlib.util.spec_from_file_location(
    "aggregate_list_integrity",
    Path(__file__).with_name("test_aggregate_list_integrity.py"),
)
integrity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(integrity)


def list_at(parameters, path):
    """The list parameter at a dotted path, or None."""
    node = parameters
    for part in path.split("."):
        node = getattr(node, "children", {}).get(part)
        if node is None:
            return None
    if isinstance(node, Parameter) and any(
        isinstance(value.value, list) for value in node.values_list
    ):
        return node
    return None


def benefit_list_totals(tax_benefit_system):
    """{total: the list it sums, or None}, from the built model.

    The same derivation as test_aggregate_list_integrity.benefit_list_totals:
    household_benefits, spm_unit_benefits, and each member of their lists, at
    any depth, that sums a gov.household list of its own name, names a list in
    its adds, or caps another total.
    """
    parameters = tax_benefit_system.parameters
    variables = tax_benefit_system.variables

    def summed_list(variable):
        own = f"gov.household.{variable}"
        if list_at(parameters, own):
            return own
        adds = getattr(variables.get(variable), "adds", None)
        if isinstance(adds, str) and list_at(parameters, adds):
            return adds
        return None

    totals = {}
    pending = ["household_benefits", "spm_unit_benefits"]
    while pending:
        variable = pending.pop()
        if variable in totals:
            continue
        totals[variable] = summed_list(variable)
        members = set(integrity.CAPPED_AGGREGATES.get(variable, ()))
        if totals[variable] is not None:
            parameter = list_at(parameters, totals[variable])
            members |= {
                member
                for value in parameter.values_list
                if isinstance(value.value, list)
                for member in value.value
            }
        pending += [
            member
            for member in sorted(members)
            if member in integrity.CAPPED_AGGREGATES or summed_list(member)
        ]
    return totals


BENEFIT_LIST_TOTALS = benefit_list_totals(system)


def formula_sources(variable):
    """Where each of a variable's formulas is defined, by first day."""
    return {
        str(start): (formula.__code__.co_filename, formula.__code__.co_firstlineno)
        for start, formula in variable.formulas.items()
    }


# --- 1. add_to_list_parameter --------------------------------------------

NAMES = st.sampled_from("abcdefgh")
DAYS = st.dates(date(2000, 1, 1), date(2040, 12, 31))


@st.composite
def dated_lists(draw):
    """A list parameter's dated values: {date: members}.

    A value can start on any day. None marks a gap, as a null does in a
    parameter file. Members can repeat, and the helper must keep them as
    they are.
    """
    starts = draw(st.lists(DAYS, min_size=1, max_size=4, unique=True))
    return {
        start.isoformat(): draw(st.none() | st.lists(NAMES, max_size=5))
        for start in sorted(starts)
    }


def list_parameter(values):
    node = ParameterNode(
        "root", data={"members": {"values": values, "metadata": {"unit": "list"}}}
    )
    return node.members


def value_on(values, day):
    """The members a dated list holds on a day, or None before its first."""
    starts = [start for start in sorted(values) if start <= day]
    return values[starts[-1]] if starts else None


def node_value(parameter, day):
    """The members the parameter's parent node returns on a day, as formulas
    read them. A node leaves out a child with no value on that day."""
    at_instant = parameter.parent(instant(day))
    return at_instant["members"] if "members" in at_instant else None


@settings(max_examples=200, deadline=None)
@given(
    values=dated_lists(),
    names=st.lists(NAMES, min_size=1, max_size=4),
    days=st.lists(DAYS, max_size=6),
)
def test_add_to_list_parameter_appends_only_missing_names(values, names, days):
    # The expectation comes from copies taken before the call. The parameter
    # holds the drawn member lists themselves, so a helper that changed them,
    # or the names, in place would otherwise move the expectation with it.
    unique_names = list(dict.fromkeys(names))
    expected = {
        start: (
            None
            if members is None
            else members + [name for name in unique_names if name not in members]
        )
        for start, members in values.items()
    }
    names_before = list(names)
    values_before = {
        start: None if members is None else list(members)
        for start, members in values.items()
    }

    parameter = list_parameter(values)
    # Core keeps the lists it reads, so the checks below that the drawn lists
    # stay unchanged see an edit the helper makes to the parameter's own.
    assert all(
        value.value is values[value.instant_str] for value in parameter.values_list
    )
    # Each value's first day and the day before it hold the stop dates the
    # helper computes, so check them along with the drawn days.
    checked = [day.isoformat() for day in days]
    for start in values:
        first_day = date.fromisoformat(start)
        checked += [first_day.isoformat(), (first_day - timedelta(days=1)).isoformat()]
    # The parent node caches what it returns for each day, and
    # Parameter.update clears that cache. Reading it now fills the cache, so a
    # helper that changed the values another way would leave the node, and the
    # formulas that read through it, with the old lists.
    for day in checked:
        assert node_value(parameter, day) == value_on(values_before, day)
    assert not parameter.modified and not parameter.parent.modified

    add_to_list_parameter(parameter, names)

    # The helper writes new lists. A clone of a parameter shares its member
    # lists (ParameterAtInstant.clone copies its dict shallowly), so a helper
    # that edited one in place would change every clone that shares it.
    assert names == names_before
    assert values == values_before
    starts = sorted(value.instant_str for value in parameter.values_list)
    assert starts == sorted(values)
    # Before a simulation serves a variable from its macro cache, it checks the
    # modified flag on each parameter or folder the variable depends on, so
    # the helper marks the parameter and each node above it.
    assert parameter.modified and parameter.parent.modified
    for day in checked:
        assert parameter(instant(day)) == value_on(expected, day)
        assert node_value(parameter, day) == value_on(expected, day)

    # CountryTaxBenefitSystem clears every flag below the root before it
    # applies a reform it is given for the second time. That call adds
    # nothing, and must mark the parameter again.
    parameter.modified = parameter.parent.modified = False
    add_to_list_parameter(parameter, names)
    assert parameter.modified and parameter.parent.modified
    for day in checked:
        assert parameter(instant(day)) == value_on(expected, day)
        assert node_value(parameter, day) == value_on(expected, day)


def test_add_to_list_parameter_keeps_dates_from_year_zero():
    parameter = list_parameter({"0000-01-01": ["a"], "2026-01-01": ["a", "b"]})
    add_to_list_parameter(parameter, ["c", "b"])
    assert parameter(instant("1990-01-01")) == ["a", "c", "b"]
    assert parameter(instant("2025-12-31")) == ["a", "c", "b"]
    assert parameter(instant("2026-01-01")) == ["a", "b", "c"]


# --- 2 to 5. The reforms ---------------------------------------------------


@pytest.fixture(scope="module", params=["baseline", *REFORMS])
def policy(request):
    """(name, system): one reformed system at a time, each about 0.7 GB."""
    gc.collect()
    name = request.param
    if name == "baseline":
        yield name, system
        return
    reformed = CountryTaxBenefitSystem(reform=REFORMS[name][0])
    yield name, reformed
    del reformed
    gc.collect()


def test_reform_lists_are_baseline_lists_plus_own_additions(policy):
    name, reformed = policy
    lists = list_parameters(reformed)
    assert lists.keys() == BASELINE_LISTS.keys()
    for parameter_name, baseline in BASELINE_LISTS.items():
        changed = lists[parameter_name]
        if not changes(name, parameter_name):
            assert dated(changed) == dated(baseline), parameter_name
            continue
        for day in breakpoints(baseline, changed):
            expected = members_on(baseline, day)
            if expected is not None:
                expected += additions(name, parameter_name, int(day[:4]))
            assert members_on(changed, day) == expected, (parameter_name, day)


def test_reformed_systems_mark_exactly_the_lists_they_change(policy):
    # The macro cache reads a modified flag as "differs from current law".
    # The fixture passes each reform to CountryTaxBenefitSystem, which clears
    # every flag below the root between its two applications of that reform.
    name, reformed = policy
    for parameter_name, parameter in list_parameters(reformed).items():
        assert parameter.modified == changes(name, parameter_name), parameter_name
    assert reformed.parameters.gov.household.modified == (name != "baseline")


def test_applying_a_reform_twice_changes_no_list(policy):
    name, reformed = policy
    if name == "baseline":
        pytest.skip("current law applies no reform")
    once = list_parameters(reformed)
    twice = list_parameters(REFORMS[name][0](reformed))
    assert twice.keys() == once.keys()
    for parameter_name, parameter in once.items():
        assert dated(twice[parameter_name]) == dated(parameter), parameter_name


def test_benefit_list_totals_match_the_integrity_test():
    assert BENEFIT_LIST_TOTALS == integrity.BENEFIT_LIST_TOTALS


def test_reforms_keep_every_benefit_list_total(policy):
    name, reformed = policy
    for total in BENEFIT_LIST_TOTALS:
        variable, baseline = reformed.variables[total], system.variables[total]
        assert not variable.is_neutralized, total
        assert variable.adds == baseline.adds, total
        assert formula_sources(variable) == formula_sources(baseline), total


def program_state(program):
    """The state whose program this is, from its prefix, or None if national."""
    prefix = program.split("_")[0].upper()
    return prefix if len(prefix) == 2 and prefix in STATES else None


@st.composite
def households(draw):
    """(state, year, {program: amount}) for a one-person household.

    The programs are drawn from the baseline SPM list, what its formula adds,
    the reforms' own benefits and the broadband subsidies, which no benefit
    list may hold.
    """
    year = draw(st.integers(2023, 2027))
    state = draw(st.sampled_from(STATES))
    candidates = [
        program
        for program in benefit_list(system, SPM, year)
        if program_state(program) in (None, state)
    ] + [*SPM_FORMULA_BENEFITS, *OWN_BENEFITS, "acp", "ebb"]
    programs = draw(st.lists(st.sampled_from(candidates), max_size=8, unique=True))
    amounts = st.integers(1, 30_000)
    return state, year, {program: draw(amounts) for program in programs}


def one_person(tax_benefit_system, state, year, earnings, inputs):
    """A one-person household, each input on its variable's entity."""
    groups = {"person": {}, "tax_unit": {}, "spm_unit": {}, "household": {}}
    for name, value in inputs.items():
        if name in tax_benefit_system.variables:
            entity = tax_benefit_system.variables[name].entity.key
            groups[entity][name] = {year: value}
    groups["person"].update(age={year: 40}, employment_income={year: earnings})
    groups["household"]["state_name"] = {year: state}
    members = ["you"]
    return {
        "people": {"you": groups["person"]},
        "tax_units": {"tax_unit": {"members": members, **groups["tax_unit"]}},
        "spm_units": {"spm_unit": {"members": members, **groups["spm_unit"]}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": members}},
        "households": {"household": {"members": members, **groups["household"]}},
    }


def summed(simulation, names, year):
    return sum(
        float(simulation.calculate(name, year, map_to="spm_unit").sum())
        for name in names
    )


# Totals run in float32, so allow for rounding; a dropped or repeated program
# moves a total by at least the $1 of its smallest amount.
ROUNDING = 0.5


@settings(max_examples=25, deadline=None)
@given(household=households())
# Programs the old reform copies dropped, and the broadband subsidies the Tlaib
# copies counted twice.
@example(household=("WY", 2027, {"wy_ssp": 240, "tx_rebate": 1_500}))
@example(household=("WA", 2026, {"wa_sfa": 1_000, "wa_rca": 500, "wa_ssp": 300}))
@example(household=("NY", 2024, {"ny_ssp": 1_052, "acp": 360, "ebb": 120}))
@example(household=("CA", 2026, {"ca_state_supplement": 2_000, "ssi": 4_000}))
def test_benefit_totals_sum_the_baseline_lists_and_own_additions(policy, household):
    name, reformed = policy
    state, year, inputs = household
    simulation = Simulation(
        tax_benefit_system=reformed,
        situation=one_person(reformed, state, year, 500_000, inputs),
    )

    spm_programs = (
        benefit_list(system, SPM, year)
        + additions(name, SPM, year)
        + SPM_FORMULA_BENEFITS
    )
    assert float(simulation.calculate("spm_unit_benefits", year).sum()) == (
        pytest.approx(summed(simulation, spm_programs, year), abs=ROUNDING)
    )

    household_programs = benefit_list(system, HOUSEHOLD, year) + (
        additions(name, HOUSEHOLD, year)
    )
    assert float(simulation.calculate("household_benefits", year).sum()) == (
        pytest.approx(summed(simulation, household_programs, year), abs=ROUNDING)
    )


@settings(max_examples=8, deadline=None)
@given(
    program=st.sampled_from(["acp", "ebb"]),
    amount=st.integers(1, 5_000),
    year=st.integers(2022, 2024),
    state=st.sampled_from(STATES),
)
def test_broadband_subsidies_reach_spm_net_income_once(
    policy, program, amount, year, state
):
    name, reformed = policy

    def net_income(value):
        simulation = Simulation(
            tax_benefit_system=reformed,
            situation=one_person(reformed, state, year, 100_000, {program: value}),
        )
        return float(simulation.calculate("spm_unit_net_income", year).sum())

    assert net_income(amount) - net_income(0) == pytest.approx(amount, abs=0.05)
