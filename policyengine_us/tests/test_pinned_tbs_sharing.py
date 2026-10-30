"""A pin copies only the parameters it edits.

New York's and Alabama's formulas recompute federal credits under an earlier
vintage. A pinned system copies the subtrees a pin edits and reads every other
parameter from the tree it came from, where a full clone would rebuild 143,000
nodes. These tests hold it to what that clone would have given:

- a pin reads what a full clone reads, for every parameter, and leaves its
  source as it found it;
- a pin built after a change to its source reads that change;
- a simulation's pinned system is its own, apart from the nodes it shares;
- a traced simulation records what it would record on a full clone;
- nothing outlives a finished simulation.

The Hypothesis test drives a tree of a few parameters. The others use the
model, so they keep to the fewest simulations that show each behaviour.
"""

import collections
import gc
import weakref

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.spm import pin_spm_policy, tree_is_shared, tree_owning_subtrees
from policyengine_us.system import CountryTaxBenefitSystem, system
from policyengine_us.tools import pinned_tbs

YEAR = 2024
AT = "2000-01-01"
START = instant(AT)
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
            "owned": {"a": parameter(1), "b": parameter(0), "scale": scale},
            "outer": {
                "owned": {"c": parameter(0)},
                "lent": {"d": parameter(1)},
            },
            "lent": parameter(1),
        },
    )


def pin_small_tree(tree):
    amount = tree.owned.scale.brackets[0].amount
    value = tree.owned.a(AT) + tree.lent(AT) + tree.outer.lent.d(AT)
    tree.owned.b.update(start=START, stop=STOP, value=value)
    tree.outer.owned.c.update(start=START, stop=STOP, value=amount(AT))


def small_tree_parameters(tree):
    return (
        tree.owned.a,
        tree.owned.scale.brackets[0].amount,
        tree.lent,
        tree.outer.lent.d,
    )


CHANGES = st.lists(
    st.one_of(
        st.tuples(st.just("read"), st.just(0), st.just(0)),
        st.tuples(st.just("edit"), st.integers(0, 3), st.integers(1, 9)),
    ),
    max_size=12,
)


@settings(deadline=None, max_examples=200)
@given(CHANGES)
def test_a_tree_owning_subtrees_reads_what_a_clone_reads(changes):
    """A brand-new pin agrees with a brand-new clone after any changes.

    Reads fill the at-instant caches an edit has to clear, and a tree straight
    from its loader has scale brackets with no parent, so an edit to a bracket
    goes no further than the bracket.
    """
    tree = small_tree()
    for change, index, value in changes:
        if change == "read":
            tree(AT)
        else:
            parameter = small_tree_parameters(tree)[index]
            parameter.update(start=START, stop=STOP, value=value)

        source_values = parameter_values(tree)
        own = tree_owning_subtrees(tree, ("owned", "outer.owned"))
        pin_small_tree(own)
        clone = tree.clone()
        pin_small_tree(clone)

        assert parameter_values(own) == parameter_values(clone)
        assert parameter_values(tree) == source_values
        assert own(AT).owned.b == clone(AT).owned.b
        assert own(AT).outer.owned.c == clone(AT).outer.owned.c
        assert own(AT).outer.lent.d == clone(AT).outer.lent.d

        assert own.lent is tree.lent and own.outer.lent is tree.outer.lent
        assert own.owned is not tree.owned
        assert own.outer.owned is not tree.outer.owned
        assert tree_is_shared(own)

        # An edit to what the pin owns reaches its root and stops there.
        own.owned.a.update(start=START, stop=STOP, value=100)
        assert own(AT).owned.a == 100
        assert parameter_values(tree) == source_values


@pytest.fixture(scope="module")
def source():
    return system.clone()


@pytest.mark.parametrize("pin_name", PINS)
def test_every_pin_reads_what_a_full_clone_reads(source, pin_name):
    """A pin that edited a node it does not own would fail here, twice."""
    pin = getattr(pinned_tbs, pin_name)
    source_values = parameter_values(source.parameters)
    pinned = pin_spm_policy(source, pinned_tbs.PINNED_SUBTREES)
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


def test_simulations_share_what_no_pin_edits():
    simulations = [Simulation(situation=household()) for _ in range(2)]
    pins = [
        pinned_tbs.get_pre_tcja_ctc_tbs(simulation.tax_benefit_system)
        for simulation in simulations
    ]

    assert pins[0] is not pins[1]
    assert pins[0].parameters.gov.states is pins[1].parameters.gov.states
    assert pins[0].parameters.gov.irs.income is pins[1].parameters.gov.irs.income
    assert pins[0].parameters.gov.irs.credits is not pins[1].parameters.gov.irs.credits


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


def test_a_pinned_system_is_private_apart_from_the_nodes_it_shares():
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
