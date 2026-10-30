"""A pin copies the parameter tree's nodes and borrows its dated values.

New York's and Alabama's formulas recompute federal credits under an earlier
vintage. A pinned system gets its own tree, whose histories hold the entries of
the tree it came from, where a full clone would rebuild all of them. These tests
hold it to what that clone would have given:

- the copied tree reads what a clone reads, whatever its source has cached, and
  neither tree sees the other's later edits;
- a pin reads what a full clone reads, for every parameter, and leaves its
  source as it found it;
- a pin built after a change to its source reads that change;
- a simulation's pinned system is its own;
- a traced simulation records what it would record on a full clone;
- nothing outlives a finished simulation, and the cache holds nothing back.

The Hypothesis test drives a tree of a few parameters. The others use the
model, so they keep to the fewest simulations that show each behaviour.
"""

import collections
import gc
import weakref

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import (
    Parameter,
    ParameterAtInstant,
    ParameterNode,
)
from policyengine_core.parameters.operations.interpolate_parameters import (
    interpolate_parameters,
)
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.spm import copy_parameter_nodes, pin_spm_policy
from policyengine_us.system import CountryTaxBenefitSystem, system
from policyengine_us.tools import pinned_tbs

YEAR = 2024
AT = "2000-01-01"
LATER = "2001-01-01"
STOP = instant("2099-12-31")
# The pins overwrite the credits' own parameters, so a change to those cannot
# show through one. This rate reaches New York's credit through the federal
# limit on the non-refundable credit, which the branch recomputes.
BOTTOM_RATE = "gov.irs.income.bracket.rates.1"
LOWER_BOTTOM_RATE = 0.05
PINS = sorted(name for name in vars(pinned_tbs) if name.startswith("_pin_"))


def household(year=YEAR, state_code="NY", earnings=6_000, interest=20_000):
    members = ["head", "child"]
    return {
        "people": {
            "head": {
                "age": {year: 40},
                "employment_income": {year: earnings},
                "taxable_interest_income": {year: interest},
            },
            "child": {"age": {year: 6}},
        },
        "tax_units": {"tax_unit": {"members": members}},
        "households": {
            "household": {"members": members, "state_code": {year: state_code}}
        },
    }


def fresh_clones():
    """What a pin stands in for: a full clone for each system and pin."""
    clones = {}

    def fresh_clone_of(base_tbs, pin_name, pin_fn):
        key = (id(base_tbs), pin_name)
        if key not in clones:
            clones[key] = base_tbs.clone()
            pin_fn(clones[key])
        return clones[key]

    return fresh_clone_of


def count_builds(monkeypatch):
    """Record the pin functions that run from now on."""
    builds = []
    get_pinned_tbs = pinned_tbs._get_pinned_tbs

    def counted(base_tbs, pin_name, pin_fn):
        def counted_pin(pinned):
            builds.append(pin_name)
            pin_fn(pinned)

        return get_pinned_tbs(base_tbs, pin_name, counted_pin)

    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", counted)
    return builds


def parameter_values(tree):
    return {
        parameter.name: [
            (item.instant_str, repr(item.value)) for item in parameter.values_list
        ]
        for parameter in tree.get_descendants()
        if isinstance(parameter, Parameter)
    }


@pytest.fixture(autouse=True)
def collect_cycles():
    # Simulations sit in reference cycles, each with its branches' systems.
    yield
    gc.collect()


def small_tree():
    def parameter(value):
        return {"values": {AT: value}}

    scale = {"brackets": [{"threshold": parameter(0), "amount": parameter(1)}]}
    return ParameterNode(
        "",
        data={
            "credit": {"amount": parameter(1), "scale": scale},
            "tax": {"rate": parameter(1)},
        },
    )


def change_small_tree(tree, change, index, value):
    """Change ``tree`` in one of the ways it can change.

    Only ``update`` clears a cache, and on a loaded tree it stops at a scale's
    bracket, which has no parent.
    """
    credit = tree.credit
    parameter = (credit.amount, credit.scale.brackets[0].amount, tree.tax.rate)[index]
    if change == "read":
        tree(LATER)
    elif change == "update":
        parameter.update(start=instant(LATER), stop=STOP, value=value)
    elif change == "add entry":
        # What interpolation and uprating do to a history.
        parameter.values_list.append(
            ParameterAtInstant(parameter.name, LATER, data=value)
        )
        parameter.values_list.sort(key=lambda item: item.instant_str, reverse=True)
    elif f"added_{value}" not in tree.tax.children:
        added = Parameter(f"added_{value}", {"values": {AT: value}})
        tree.tax.add_child(f"added_{value}", added)


def small_tree_readings(tree):
    view = tree(LATER)
    scale = view.credit.scale
    added = sorted(name for name in tree.tax.children if name != "rate")
    return (
        view.credit.amount,
        view.tax.rate,
        list(scale.amounts),
        list(scale.thresholds),
        [getattr(view.tax, name) for name in added],
    )


def nodes_of(tree):
    return [tree, *tree.get_descendants()]


def root_of(node):
    while node.parent is not None:
        node = node.parent
    return node


CHANGES = st.lists(
    st.tuples(
        st.sampled_from(["read", "update", "add entry", "add child"]),
        st.integers(0, 2),
        st.integers(1, 9),
    ),
    max_size=12,
)


@settings(deadline=None, max_examples=200)
@given(CHANGES, CHANGES)
def test_a_copy_of_the_nodes_reads_what_a_clone_reads(changes, later_changes):
    """A copy agrees with a clone after any changes, and then goes its own way.

    The reads fill the at-instant caches that most of the changes leave stale,
    which a tree that shared a node with its source would go on reading.
    """
    tree = small_tree()
    for change in changes:
        change_small_tree(tree, *change)

    copied = copy_parameter_nodes(tree)
    clone = tree.clone()

    assert parameter_values(copied) == parameter_values(clone)
    assert small_tree_readings(copied) == small_tree_readings(clone)

    # It shares no node with its source, and every edit reaches its own root.
    assert not {id(node) for node in nodes_of(tree)} & {
        id(node) for node in nodes_of(copied)
    }
    for node in nodes_of(copied):
        assert root_of(node) is copied
        for name, child in getattr(node, "children", {}).items():
            assert getattr(node, name) is child

    copied_values = parameter_values(copied)
    for change in later_changes:
        change_small_tree(tree, *change)
    assert parameter_values(copied) == copied_values

    tree_values = parameter_values(tree)
    for change in later_changes:
        change_small_tree(copied, *change)
    assert parameter_values(tree) == tree_values


@pytest.fixture(scope="module")
def source():
    return system.clone()


@pytest.mark.parametrize("pin_name", PINS)
def test_every_pin_reads_what_a_full_clone_reads(source, pin_name):
    """A pin that wrote through to a borrowed entry would fail here, twice."""
    pin = getattr(pinned_tbs, pin_name)
    source_values = parameter_values(source.parameters)
    pinned = pin_spm_policy(source)
    pin(pinned)
    clone = source.clone()
    pin(clone)

    assert parameter_values(pinned.parameters) == parameter_values(clone.parameters)
    assert parameter_values(source.parameters) == source_values


def test_a_simulation_builds_each_pin_once(monkeypatch):
    builds = count_builds(monkeypatch)
    simulation = Simulation(situation=household())
    simulation.calculate("ny_ctc", YEAR)
    simulation.calculate("ny_ctc", YEAR + 1)

    assert builds == ["ny_pre_tcja_ctc"]


def test_a_pin_borrows_every_dated_value(monkeypatch, source):
    """What a pin saves on a clone is not rebuilding the histories."""

    def fail(entry):
        raise AssertionError(f"rebuilt {entry.name}")

    monkeypatch.setattr(ParameterAtInstant, "clone", fail)
    pinned = pin_spm_policy(source)

    rate = pinned.parameters.get_child(BOTTOM_RATE)
    source_rate = source.parameters.get_child(BOTTOM_RATE)
    assert rate is not source_rate
    assert rate.values_list is not source_rate.values_list
    assert all(a is b for a, b in zip(rate.values_list, source_rate.values_list))
    assert pinned.shares_parameters and source.shares_parameters


def test_each_pin_is_cached_for_the_last_system_that_asked():
    """A change no check sees, in place on a variable, ends with the entry."""
    first, second = [
        Simulation(situation=household()).tax_benefit_system for _ in range(2)
    ]
    pin = pinned_tbs.get_pre_tcja_ctc_tbs(first)
    assert pinned_tbs.get_pre_tcja_ctc_tbs(first) is pin

    other = pinned_tbs.get_pre_tcja_ctc_tbs(second)
    assert other is not pin
    assert pinned_tbs.get_pre_tcja_ctc_tbs(first) is not pin


@pytest.mark.parametrize(
    "state_code, year, earnings, interest, variable",
    [
        ("NY", 2024, 6_000, 20_000, "ny_ctc"),
        ("NY", 2021, 6_000, 0, "ny_eitc"),
        ("AL", 2021, 60_000, 0, "al_federal_income_tax_deduction"),
    ],
)
def test_a_pin_gives_what_a_fresh_clone_gives(
    monkeypatch, state_code, year, earnings, interest, variable
):
    def result():
        simulation = Simulation(
            situation=household(year, state_code, earnings, interest)
        )
        return simulation.calculate(variable, year)[0]

    pinned = result()
    assert pinned != 0
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert pinned == result()


def test_a_reform_reaches_only_the_simulation_that_applied_it():
    def credit_and_pinned_rate(reform=None):
        simulation = Simulation(situation=household())
        if reform is not None:
            simulation.apply_reform(reform)
        credit = simulation.calculate("ny_ctc", YEAR)[0]
        pin = pinned_tbs.get_pre_tcja_ctc_tbs(simulation.tax_benefit_system)
        rate = pin.parameters.get_child(BOTTOM_RATE)(f"{YEAR}-01-01")
        del simulation, pin
        # Each step's trees go before the next step builds its own.
        gc.collect()
        return credit, rate

    before = credit_and_pinned_rate()
    credit, rate = credit_and_pinned_rate({BOTTOM_RATE: {str(YEAR): LOWER_BOTTOM_RATE}})

    assert credit != before[0]
    assert rate == LOWER_BOTTOM_RATE
    assert credit_and_pinned_rate() == before


def test_an_edit_to_the_source_tree_reaches_the_next_simulation(monkeypatch):
    """A simulation reads an in-place edit at once, so a pin has to as well.

    Only the pin's own copy of the rate could leave the result behind here, as
    the simulation itself reads the edited tree.
    """
    supplied = system.clone()

    def result():
        simulation = Simulation(situation=household(), tax_benefit_system=supplied)
        credit = simulation.calculate("ny_ctc", YEAR)[0]
        del simulation
        gc.collect()
        return credit

    before = result()
    rate = supplied.parameters.get_child(BOTTOM_RATE)
    rate.update(period=f"year:{YEAR}:1", value=LOWER_BOTTOM_RATE)
    edited = result()

    assert edited != before
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert result() == edited


def test_an_edit_to_a_loaded_tree_reaches_the_next_simulation(monkeypatch):
    """A loaded tree's scale brackets have no parent, unlike a clone's.

    So this edit clears no cache above the bracket, and a pin has to read the
    parameter itself. The EITC's 2021 pin keeps this amount, so its result
    moves with the edit.
    """
    loaded = CountryTaxBenefitSystem()
    assert loaded.parameters.gov.irs.credits.eitc.max.brackets[1].parent is None

    def result():
        situation = household(2021, earnings=15_000, interest=0)
        simulation = Simulation(situation=situation, tax_benefit_system=loaded)
        return simulation.calculate("ny_eitc", 2021)[0]

    before = result()
    amount = loaded.parameters.gov.irs.credits.eitc.max.brackets[1].amount
    amount.update(period="year:2021:1", value=5_000)
    edited = result()

    assert edited != before
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert result() == edited


def test_a_pin_reads_past_a_view_its_source_has_left_stale(monkeypatch):
    """Interpolation adds to a history and clears no cache.

    So the source goes on serving the view it cached, and a pin reads the new
    entry only because the view it builds is its own, as a clone's is.
    """
    supplied = system.clone()
    rate = supplied.parameters.get_child(BOTTOM_RATE)
    rate.values_list = [
        ParameterAtInstant(rate.name, f"{year}-01-01", data=value)
        for year, value in ((2025, 0.2), (2023, 0.01))
    ]
    rate.metadata["interpolation"] = {"interval": "year"}

    def result():
        simulation = Simulation(situation=household(), tax_benefit_system=supplied)
        credit = simulation.calculate("ny_ctc", YEAR)[0]
        del simulation
        gc.collect()
        return credit

    before = result()
    interpolate_parameters(supplied.parameters)
    interpolated = result()

    assert rate(f"{YEAR}-01-01") == pytest.approx(0.105)
    assert interpolated != before
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert result() == interpolated


def test_a_reform_of_the_source_leaves_a_built_pin_alone():
    """This system owns its tree, so only pinning stops a reform writing in place.

    The reform has to change the tree's identity for the next pin to notice it.
    """
    policy = system.clone()
    pin = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    def rate(pinned):
        return pinned.parameters.get_child(BOTTOM_RATE)(f"{YEAR}-01-01")

    def lower_rate(parameters):
        parameters.get_child(BOTTOM_RATE).update(
            period=f"year:{YEAR}:1", value=LOWER_BOTTOM_RATE
        )
        return parameters

    before = rate(pin)
    policy.modify_parameters(lower_rate)

    assert rate(pin) == before != LOWER_BOTTOM_RATE
    assert rate(pinned_tbs.get_pre_tcja_ctc_tbs(policy)) == LOWER_BOTTOM_RATE


def test_a_pinned_system_is_its_own():
    first = Simulation(situation=household())
    second = Simulation(situation=household(), spm={"geography_kind": "national"})
    policies = [first.tax_benefit_system, second.tax_benefit_system]
    pins = [pinned_tbs.get_pre_tcja_ctc_tbs(policy) for policy in policies]

    assert pins[0].spm_forecast_provider is not policies[0].spm_forecast_provider
    assert pins[0].spm_forecast_provider.geography_kind != "national"
    assert pins[1].spm_forecast_provider.geography_kind == "national"
    for pin, policy in zip(pins, policies):
        assert all(entity._tax_benefit_system is pin for entity in pin.entities)
        assert set(pin.variables) == set(policy.variables)
        # A clone's variables, as core's own clone keeps them.
        assert pin.variables["ctc"] is not policy.variables["ctc"]
        assert pin.variables["ctc"].entity._tax_benefit_system is pin


def test_a_pinned_system_does_not_inherit_unpinned_at_instant_reads():
    policy = Simulation(situation=household()).tax_benefit_system
    instant_read = f"{YEAR}-01-01"
    credit = policy.get_parameters_at_instant(instant_read).gov.irs.credits.ctc
    assert credit.refundable.individual_max != 1_000

    pinned = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    credit = pinned.get_parameters_at_instant(instant_read).gov.irs.credits.ctc
    assert credit.refundable.individual_max == 1_000


def test_a_pin_follows_a_variable_reform_applied_after_it_was_built():
    class NeutralizeLimit(Reform):
        def apply(self):
            self.neutralize_variable("ctc_limiting_tax_liability")

    simulation = Simulation(situation=household())
    policy = simulation.tax_benefit_system
    before = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    simulation.apply_reform(NeutralizeLimit)
    after = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    assert not before.variables["ctc_limiting_tax_liability"].is_neutralized
    assert after.variables["ctc_limiting_tax_liability"].is_neutralized


@pytest.mark.parametrize("trace", [False, True])
def test_nothing_outlives_a_finished_simulation(trace):
    simulation = Simulation(situation=household(), trace=trace)
    simulation.calculate("ny_ctc", YEAR)
    finished = weakref.ref(simulation)
    policy = weakref.ref(simulation.tax_benefit_system)
    pinned = weakref.ref(pinned_tbs.get_pre_tcja_ctc_tbs(simulation.tax_benefit_system))
    tracer = weakref.ref(simulation.tracer)
    del simulation
    gc.collect()

    assert finished() is None
    assert policy() is None
    assert pinned() is None
    assert tracer() is None


def test_a_simulation_built_on_a_pin_lets_go_of_the_one_it_came_from():
    simulation = Simulation(situation=household())
    pin = pinned_tbs.get_pre_tcja_ctc_tbs(simulation.tax_benefit_system)
    built_on_pin = Simulation(situation=household(), tax_benefit_system=pin, reform={})
    finished = weakref.ref(simulation)
    del simulation, pin
    gc.collect()

    assert finished() is None
    assert built_on_pin.tax_benefit_system is not None


def test_a_traced_simulation_records_what_a_fresh_clone_records(monkeypatch):
    def recorded_reads():
        simulation = Simulation(situation=household(), trace=True)
        simulation.calculate("ny_ctc", YEAR)
        reads = collections.Counter()
        nodes = list(simulation.tracer.trees)
        while nodes:
            node = nodes.pop()
            nodes.extend(node.children)
            reads.update(
                (node.branch_name, read.name, str(read.period), repr(read.value))
                for read in node.parameters
            )
        return reads

    pinned = recorded_reads()
    assert any(branch == "pre_tcja_ctc" for branch, *_ in pinned)
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert pinned == recorded_reads()


def test_a_traced_simulation_leaves_an_ordinary_one_untraced():
    traced = Simulation(situation=household(), trace=True)
    traced.calculate("ny_ctc", YEAR)

    ordinary = Simulation(situation=household())
    ordinary.calculate("ny_ctc", YEAR)
    pin = pinned_tbs.get_pre_tcja_ctc_tbs(ordinary.tax_benefit_system)

    assert pin.parameters.trace is False
    assert pinned_tbs.get_pre_tcja_ctc_tbs(traced.tax_benefit_system).parameters.trace
