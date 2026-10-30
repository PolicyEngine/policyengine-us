"""One pinned parameter tree serves every simulation that reads the same tree.

New York's and Alabama's formulas recompute federal credits under an earlier
vintage. A simulation's own system differs from the next one's, but both read
one parameter tree, so a pin belongs to that tree. These tests hold the cache
to what a fresh clone would have given:

- a pin reflects the source tree as it stands now, however the tree changed;
- a pin is built once while its source tree stands still;
- a simulation's pinned system is its own, apart from the tree;
- the cache keeps nothing of a finished simulation.

The Hypothesis test drives the cache on a tree of a few parameters. The others
use the model, at about 0.5 GB and several seconds for each tree they build,
so they keep to the fewest simulations that show each behaviour.
"""

import gc
import weakref

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.spm import mark_tree_shared, share_spm_policy, tree_is_shared
from policyengine_us.system import system
from policyengine_us.tools import pinned_tbs

YEAR = 2024
START = instant("2000-01-01")
STOP = instant("2099-12-31")
# The pins overwrite the credits' own parameters, so a change to those cannot
# show through one. This rate reaches New York's credit through the federal
# limit on the non-refundable credit, which the branch recomputes.
BOTTOM_RATE = "gov.irs.income.bracket.rates.1"
LOWER_BOTTOM_RATE = 0.05


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
    """What the cache stands in for: a new clone for each system and pin."""
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


@pytest.fixture(autouse=True)
def empty_cache():
    """Start each test with no pins, and hand the next file what it left."""
    cached = dict(pinned_tbs._PINNED_TBS_CACHE)
    pinned_tbs._PINNED_TBS_CACHE.clear()
    yield
    pinned_tbs._PINNED_TBS_CACHE.clear()
    pinned_tbs._PINNED_TBS_CACHE.update(cached)
    # Simulations sit in reference cycles, each with its branches' systems.
    gc.collect()


def small_tree(a):
    return mark_tree_shared(
        ParameterNode(
            "",
            data={
                "a": {"values": {"2000-01-01": a}},
                "b": {"values": {"2000-01-01": 0}},
            },
        )
    )


def double_a_into_b(pinned):
    parameters = pinned.parameters
    parameters.b.update(start=START, stop=STOP, value=2 * parameters.a("2000-01-01"))


def reader_of(tree):
    reader = share_spm_policy(system)
    reader.parameters = tree
    return reader


OPERATIONS = st.lists(
    st.one_of(
        st.tuples(st.just("read"), st.integers(0, 3)),
        st.tuples(st.just("new reader"), st.integers(0, 1)),
        st.tuples(st.just("edit"), st.integers(0, 3), st.integers(1, 9)),
        st.tuples(st.just("reform"), st.integers(0, 3)),
    ),
    max_size=12,
)


@settings(
    deadline=None,
    max_examples=60,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(OPERATIONS)
def test_pin_matches_its_source_after_any_sequence_of_changes(operations):
    """Hold the cache, step by step, to a model of what it should do.

    The model records which tree, and which edit of it, the last build used.
    A read builds exactly when that changed, and it returns a pin of the source
    as the source stands, leaving the source alone.
    """
    pinned_tbs._PINNED_TBS_CACHE.clear()
    trees = [small_tree(1), small_tree(2)]
    readers = [reader_of(trees[0]), reader_of(trees[1])]
    edits = {id(tree): 0 for tree in trees}
    built_from = None
    builds = 0
    # Readers of one tree can hold identical variables, as these do, and each
    # still needs a pinned system of its own for its receipts.
    reader_of_pin = {}

    def counted_pin(pinned):
        nonlocal builds
        builds += 1
        double_a_into_b(pinned)

    for operation, index, *value in operations:
        if operation == "new reader":
            readers.append(reader_of(trees[index]))
            continue
        reader = readers[index % len(readers)]
        if operation == "edit":
            reader.parameters.a.update(start=START, stop=STOP, value=value[0])
            edits[id(reader.parameters)] += 1
        elif operation == "reform":
            with reader.detaching_parameters():
                detached = reader.parameters
            trees.append(detached)
            edits.setdefault(id(detached), 0)
        else:
            source = reader.parameters
            b_before = source.b("2000-01-01")
            before = builds
            pinned = pinned_tbs._get_pinned_tbs(reader, "small", counted_pin)

            state = (id(source), edits[id(source)])
            assert builds - before == (0 if state == built_from else 1)
            built_from = state
            assert pinned.parameters is not source
            assert pinned.parameters.b("2000-01-01") == 2 * source.a("2000-01-01")
            assert source.b("2000-01-01") == b_before
            assert pinned.variables == reader.variables
            assert reader_of_pin.setdefault(pinned, reader) is reader
            assert pinned is pinned_tbs._get_pinned_tbs(reader, "small", counted_pin)


def test_a_process_of_simulations_builds_each_pin_once(monkeypatch):
    builds = count_builds(monkeypatch)
    simulations = [Simulation(situation=household()) for _ in range(2)]
    results = [simulation.calculate("ny_ctc", YEAR)[0] for simulation in simulations]

    assert builds == ["ny_pre_tcja_ctc"]
    assert results[0] == results[1]
    pins = [
        pinned_tbs.get_pre_tcja_ctc_tbs(simulation.tax_benefit_system)
        for simulation in simulations
    ]
    assert pins[0] is not pins[1]
    assert pins[0].parameters is pins[1].parameters


@pytest.mark.parametrize(
    "state_code, year, earnings, interest, variable",
    [
        ("NY", 2024, 6_000, 20_000, "ny_ctc"),
        ("NY", 2021, 6_000, 0, "ny_eitc"),
        ("AL", 2021, 60_000, 0, "al_federal_income_tax_deduction"),
    ],
)
def test_a_shared_pin_gives_what_a_fresh_clone_gives(
    monkeypatch, state_code, year, earnings, interest, variable
):
    """Compare with the clone this cache replaces.

    The second simulation runs on the pinned tree the first one built, and on
    its own variables, entities and receipts.
    """

    def result():
        simulation = Simulation(
            situation=household(year, state_code, earnings, interest)
        )
        return simulation.calculate(variable, year)[0]

    result()
    shared = result()
    assert shared != 0
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert shared == result()


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


def test_an_edit_to_the_source_tree_rebuilds_the_pin(monkeypatch):
    """A simulation reads an in-place edit at once, so a pin has to as well.

    Only the pin's own copy of the rate could leave the result behind here, as
    the simulation itself reads the edited tree.
    """
    builds = count_builds(monkeypatch)
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

    assert builds == ["ny_pre_tcja_ctc", "ny_pre_tcja_ctc"]
    assert edited != before
    monkeypatch.setattr(pinned_tbs, "_get_pinned_tbs", fresh_clones())
    assert result() == edited


def test_a_pinned_system_is_private_apart_from_the_tree():
    first = Simulation(situation=household())
    second = Simulation(situation=household(), spm={"geography_kind": "national"})
    policies = [first.tax_benefit_system, second.tax_benefit_system]
    pins = [pinned_tbs.get_pre_tcja_ctc_tbs(policy) for policy in policies]

    assert pins[0].parameters is pins[1].parameters
    assert tree_is_shared(pins[0].parameters)
    assert pins[0].variables is not pins[1].variables
    assert all(entity._tax_benefit_system is pins[0] for entity in pins[0].entities)
    assert pins[0].spm_forecast_provider is not policies[0].spm_forecast_provider
    assert pins[0].spm_forecast_provider.geography_kind != "national"
    assert pins[1].spm_forecast_provider.geography_kind == "national"
    # Every simulation rebuilds its structural reform's variables at its own
    # start instant, so each pin has to carry that simulation's own.
    for pin, policy in zip(pins, policies):
        assert pin.variables == policy.variables


def test_a_pinned_system_does_not_inherit_unpinned_at_instant_reads():
    policy = Simulation(situation=household()).tax_benefit_system
    instant_read = f"{YEAR}-01-01"
    credit = policy.get_parameters_at_instant(instant_read).gov.irs.credits.ctc
    assert credit.refundable.individual_max != 1_000

    pinned = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    credit = pinned.get_parameters_at_instant(instant_read).gov.irs.credits.ctc
    assert credit.refundable.individual_max == 1_000


def test_a_pin_follows_a_variable_reform_applied_after_it_was_built(monkeypatch):
    builds = count_builds(monkeypatch)

    class NeutralizeLimit(Reform):
        def apply(self):
            self.neutralize_variable("ctc_limiting_tax_liability")

    simulation = Simulation(situation=household())
    policy = simulation.tax_benefit_system
    before = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    simulation.apply_reform(NeutralizeLimit)
    after = pinned_tbs.get_pre_tcja_ctc_tbs(policy)

    assert after.variables == policy.variables
    assert after.variables != before.variables
    assert after.parameters is before.parameters
    assert builds == ["ny_pre_tcja_ctc"]


def test_the_cache_keeps_nothing_of_a_finished_simulation():
    simulation = Simulation(situation=household())
    simulation.calculate("ny_ctc", YEAR)
    finished = weakref.ref(simulation)
    policy = weakref.ref(simulation.tax_benefit_system)
    del simulation
    gc.collect()

    assert finished() is None
    assert policy() is None
    assert pinned_tbs._PINNED_TBS_CACHE


def test_a_traced_simulation_and_an_ordinary_one_keep_their_trees_apart():
    def pin_of(simulation):
        return pinned_tbs.get_pre_tcja_ctc_tbs(simulation.tax_benefit_system)

    ordinary = Simulation(situation=household())
    expected = ordinary.calculate("ny_ctc", YEAR)[0]
    tree = pin_of(ordinary).parameters

    traced = Simulation(situation=household(), trace=True)
    assert traced.calculate("ny_ctc", YEAR)[0] == expected

    later = Simulation(situation=household())
    assert later.calculate("ny_ctc", YEAR)[0] == expected
    assert tree.trace is False
    assert pin_of(later).parameters.trace is False
