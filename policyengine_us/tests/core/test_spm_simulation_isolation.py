"""One simulation's reform, clone or trace must not reach another's.

Every test here reproduces a defect an external review found on the shipped
2.0.1 runtime, where ordinary simulations share the default policy state.
"""

import hashlib
from copy import copy

import pytest
from policyengine_core.periods import YEAR
from policyengine_core.reforms import Reform
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_core.variables import Variable

from policyengine_us import Simulation
from policyengine_us.entities import Person
from policyengine_us.spm import clone_spm_system, share_spm_policy
from policyengine_us.system import system
from policyengine_us.tools.pinned_tbs import get_pre_arpa_eitc_tbs

SINGLE_STANDARD_DEDUCTION = "gov.irs.deductions.standard.amount.SINGLE"
BASELINE_INCOME_TAX = 4_016
REFORMED_INCOME_TAX = 3_718


def earner_situation():
    return {
        "people": {"person": {"age": {2024: 40}, "employment_income": {2024: 50_000}}},
        "households": {
            "household": {"members": ["person"], "county_fips": {2024: "06037"}}
        },
    }


def parameter_fingerprint(policy):
    """Digest every authored parameter value, so a shared-tree edit is visible."""
    digest = hashlib.sha256()
    for parameter in policy.parameters.get_descendants():
        values = getattr(parameter, "values_list", None)
        if values is None:
            continue
        digest.update(parameter.name.encode())
        for value_at_instant in values:
            digest.update(
                f"|{value_at_instant.instant_str}={value_at_instant.value}".encode()
            )
    return digest.hexdigest()


def parameter_accesses(tracer):
    """Every parameter name this tracer recorded, at any depth."""
    recorded = []

    def visit(node):
        recorded.extend(parameter.name for parameter in node.parameters)
        for child in node.children:
            visit(child)

    for tree in tracer.trees:
        visit(tree)
    return recorded


class NeutralizeIncomeTax(Reform):
    def apply(self):
        self.neutralize_variable("income_tax")


class clone_only_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Income input added only by the test reform"


class AddedInputReform(Reform):
    def apply(self):
        self.update_variable(clone_only_income)


def test_parameter_reform_leaves_every_other_simulation_unreformed():
    """A reform applied to one simulation must not change the shipped policy.

    Core's ``Simulation.apply_reform`` calls ``reform.apply(system)`` directly
    rather than constructing the reform, so it bypasses the defensive parameter
    clone in ``Reform.__init__`` and edits whatever tree the system hands it.
    On a shared tree that silently re-based every other simulation - including
    ones already built and calculated - onto the reformed parameter.
    """
    fingerprint_before = parameter_fingerprint(system)
    reformed = Simulation(situation=earner_situation())
    unrelated = Simulation(situation=earner_situation())
    assert reformed.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX
    assert unrelated.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX

    reformed.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert reformed.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX
    # An existing simulation, recomputed from its own inputs. Use the same
    # purge apply_reform performs: deleting one variable's arrays leaves the
    # cached intermediates that a contaminated tree would have to flow through.
    unrelated._invalidate_all_caches()
    assert unrelated.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX
    assert unrelated.calculate("standard_deduction", 2024)[0] < 100_000
    # And one built after the reform.
    later = Simulation(situation=earner_situation())
    assert later.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX
    # Nothing reached the shared instance itself.
    assert parameter_fingerprint(system) == fingerprint_before


def test_parameter_reform_detaches_the_shared_tree_and_its_warm_caches():
    simulation = Simulation(situation=earner_situation())
    policy = simulation.tax_benefit_system
    assert policy.parameters is system.parameters
    assert policy._parameters_at_instant_cache is system._parameters_at_instant_cache

    simulation.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert policy.parameters is not system.parameters
    assert policy._parameters_at_instant_cache is not (
        system._parameters_at_instant_cache
    )
    assert not policy.shares_parameters


def test_variable_only_reform_keeps_sharing_the_parameter_tree():
    """Detaching rebuilds 130,000 parameter nodes, so it must stay lazy.

    Every simulation re-applies the structural reform at its own start instant,
    and that reform only rebinds variables. Detaching for it would put a full
    tree clone on every household API request.
    """
    simulation = Simulation(situation=earner_situation())
    policy = simulation.tax_benefit_system

    simulation.apply_reform(NeutralizeIncomeTax)

    assert simulation.calculate("income_tax", 2024)[0] == 0
    assert policy.parameters is system.parameters
    assert policy.shares_parameters


def test_shared_policy_branch_follows_its_parents_parameter_reform():
    """A branch cloned without its own system shares policy deliberately."""
    simulation = Simulation(situation=earner_situation())
    branch = simulation.get_branch("shared_policy")

    simulation.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert branch.tax_benefit_system.parameters is (
        simulation.tax_benefit_system.parameters
    )
    assert branch.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX
    isolated = simulation.get_branch("separate_policy", clone_system=True)
    assert isolated.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX


def test_clone_method_aliases_calculate_on_the_clone():
    """``calc`` is documented as ``calculate``; core copies it as a bound method.

    Core keeps ``self.calc = self.calculate`` and
    ``self.df = self.calculate_dataframe`` in the instance dictionary and its
    ``clone`` copies that dictionary verbatim, so every alias on the clone
    still called the original simulation, under the original's policy.
    """
    original = Simulation(situation=earner_situation())
    assert original.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX
    clone = original.clone()
    clone.apply_reform(NeutralizeIncomeTax)

    assert clone.calculate("income_tax", 2024)[0] == 0
    assert clone.calc("income_tax", 2024)[0] == 0
    assert clone.calc.__self__ is clone
    assert clone.df.__self__ is clone
    # The original keeps its own policy and its own answer.
    assert original.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX


def test_clone_method_alias_records_receipts_on_the_clone():
    original = Simulation(situation=earner_situation())
    clone = original.clone()

    clone.calc("spm_unit_spm_threshold", 2025)

    assert set(clone.spm_provenance()["years"]) == {"2025"}
    assert original.spm_provenance()["years"] == {}


def test_reform_added_variable_accepts_input_on_an_ordinary_simulation():
    """A population asks its entity for a variable before it builds a holder.

    The entity resolves the name through the system it is bound to, so a shared
    system whose entities still belonged to the shared instance raised
    ``VariableNotFoundError`` for a variable its own registry plainly held.
    """
    simulation = Simulation(situation=earner_situation())
    simulation.apply_reform(AddedInputReform)

    simulation.set_input("clone_only_income", 2024, [123])

    assert simulation.calculate("clone_only_income", 2024)[0] == 123
    assert "clone_only_income" not in system.variables


@pytest.mark.parametrize("period", [2033, 2034])
def test_traced_simulations_record_their_own_parameter_accesses(period):
    """Core marks the parameter tree with the requesting simulation's tracer.

    On a shared tree the second traced request reused the first request's
    cached tracing node, so its parameter accesses were recorded against the
    first request's tracer - or, with that request's trace frame closed,
    recorded nowhere - and the shared tree kept a finished request's tracer for
    every simulation that read it afterwards.

    The isolation is keyed on ``trace``: setting it re-primes this request's
    root with an empty at-instant cache. Replacing a tracer in place afterwards
    is not covered - neither a bare ``simulation.tracer = ...`` write nor a
    ``parameters.tracer`` write on a system - because core memoises the
    ``TracingParameterNodeAtInstant`` in the root's ``_at_instant_cache`` bound
    to whichever tracer built it, and core's per-formula soft recast in
    ``Simulation._run_formula`` refreshes the root's own ``trace``/``tracer``
    fields without rebuilding that memo. #9448's
    ``test_cached_formula_trace_binds_replacement_tracer`` and
    ``test_system_parameter_lookup_does_not_cache_tracer`` assert that case;
    both fail against this mechanism and are not carried, because passing them
    means rebinding the memo at lookup, which is #9448's mechanism rather than
    this one. The only bare tracer write left in this package is
    ``tools/branched_simulation.py``, which nothing constructs.
    """
    first = Simulation(situation=earner_situation())
    first.trace = True
    first.calculate("spm_unit_fpg", period)
    first_accesses = parameter_accesses(first.tracer)

    second = Simulation(situation=earner_situation())
    second.trace = True
    second.calculate("spm_unit_fpg", period)

    expected = {
        "gov.abolitions.spm_unit_fpg",
        "gov.abolitions.spm_unit_size",
        "gov.hhs.fpg.additional_person",
        "gov.hhs.fpg.first_person",
    }
    assert set(first_accesses) == expected
    assert set(parameter_accesses(second.tracer)) == expected
    # The first simulation's trace did not grow when the second one calculated.
    assert parameter_accesses(first.tracer) == first_accesses
    # Each traced request owns the root node core writes its tracer onto.
    first_root = first.tax_benefit_system.parameters
    second_root = second.tax_benefit_system.parameters
    assert first_root is not second_root
    assert first_root._at_instant_cache is not second_root._at_instant_cache
    assert first_root.tracer is first.tracer
    assert second_root.tracer is second.tracer


def test_tracing_leaves_the_shared_parameter_tree_untraced():
    traced = Simulation(situation=earner_situation())
    traced.trace = True
    traced.calculate("spm_unit_fpg", 2035)

    assert traced.tax_benefit_system.parameters is not system.parameters
    assert system.parameters.trace is False
    assert system.parameters.tracer is None
    assert system.parameters.branch_name is None
    # Tracing changes no answer.
    untraced = Simulation(situation=earner_situation())
    assert (
        untraced.calculate("spm_unit_fpg", 2035)[0]
        == (traced.calculate("spm_unit_fpg", 2035)[0])
    )


def test_cloning_a_shared_policy_system_stops_sharing_its_tree():
    """Core's clone writes the cloned tree into the instance dictionary.

    A shared system resolves ``parameters`` through a property, which would
    shadow that write and hand back a "clone" still sharing the lender's tree,
    with nothing raised.

    The clone keeps the barrier rather than reverting to a plain system: it is
    the sole reader of its own tree, so nothing is marked shared and no copy is
    owed, but the tree can acquire readers later and must then be copied before
    it is written. See
    ``test_a_clone_keeps_the_copy_on_write_barrier_its_parent_had``.
    """
    shared = Simulation(situation=earner_situation()).tax_benefit_system
    assert shared.parameters is system.parameters

    cloned = shared.clone()

    assert cloned.parameters is not system.parameters
    assert not getattr(cloned, "shares_parameters", False)
    assert cloned.__dict__["shared_parameters"] is cloned.parameters
    assert parameter_fingerprint(cloned) == parameter_fingerprint(system)


def test_shared_policy_class_has_an_import_path():
    """A class only reachable from a dictionary cannot be pickled or named.

    Sharing policy puts every simulation's system on a class this module
    creates at run time, so that class has to be published under its own name -
    otherwise anything that pickles a system (a worker pool, joblib, a notebook
    checkpoint) fails on the class itself rather than on its contents.
    """
    import pickle

    import policyengine_us.spm as spm

    shared_class = type(Simulation(situation=earner_situation()).tax_benefit_system)

    assert shared_class.__module__ == spm.__name__
    assert getattr(spm, shared_class.__qualname__) is shared_class
    assert pickle.loads(pickle.dumps(shared_class)) is shared_class


def test_parameter_reform_on_a_shared_branch_leaves_its_parent_alone():
    """A branch that reforms policy owns the tree it reformed."""
    simulation = Simulation(situation=earner_situation())
    branch = simulation.get_branch("reformed_branch")

    branch.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert branch.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX
    assert simulation.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX
    assert simulation.tax_benefit_system.parameters is system.parameters


@pytest.mark.parametrize(
    "mutate",
    [
        lambda policy: policy.modify_parameters(
            {SINGLE_STANDARD_DEDUCTION: {"year:2024:1": 100_000}}
        ),
        lambda policy: policy.add_abolition_parameters(),
        # Core's load_extension ends in ``self.parameters.merge(...)``. Stub
        # the base out: a real extension is not needed to pin that this
        # country override detaches before core reaches the tree.
        lambda policy: policy.load_extension("any_extension"),
    ],
    ids=["modify_parameters", "add_abolition_parameters", "load_extension"],
)
def test_in_place_parameter_edits_detach_before_they_write(mutate, monkeypatch):
    """Core edits these into the live tree rather than a copy of it."""
    monkeypatch.setattr(
        TaxBenefitSystem, "load_extension", lambda self, extension: None
    )
    fingerprint_before = parameter_fingerprint(system)
    policy = Simulation(situation=earner_situation()).tax_benefit_system

    mutate(policy)

    assert policy.parameters is not system.parameters
    assert parameter_fingerprint(system) == fingerprint_before


def test_shared_policy_over_a_core_cloning_base_clones_without_sharing():
    """A base that clones through core must not defeat the property.

    Core's ``TaxBenefitSystem.clone`` writes the cloned tree straight into the
    new instance's dictionary, where ``SharedParameterPolicy.parameters``
    shadows it, so a system built on a base that uses core's clone would hand
    back a "clone" still reading the lender's tree, with nothing raised.
    """
    base = copy(system)
    base.__class__ = type(
        "CoreCloningCountrySystem",
        (type(system),),
        {"clone": TaxBenefitSystem.clone},
    )
    shared = share_spm_policy(base)
    assert shared.parameters is system.parameters

    cloned = shared.clone()

    assert cloned.parameters is not system.parameters
    assert parameter_fingerprint(cloned) == parameter_fingerprint(system)


def test_cloned_systems_hold_one_entity_object_per_key():
    """Core's clone leaves two objects per group-entity key, both bound.

    Rebinding through ``entities`` would then miss the copy that
    ``instantiate_entities`` and core's simulation builder read.
    """
    cloned = clone_spm_system(system)

    by_key = {entity.key: entity for entity in cloned.entities}
    assert len(by_key) == len(cloned.entities)
    assert cloned.person_entity is by_key[cloned.person_entity.key]
    assert all(entity is by_key[entity.key] for entity in cloned.group_entities)
    for entity in cloned.entities:
        assert entity._tax_benefit_system is cloned


def test_pinned_systems_are_rebuilt_when_their_source_tree_detaches():
    """A shared system keeps its identity while swapping its tree.

    The NY EITC and CTC formulas reuse a cached clone pinned to an earlier
    federal vintage. Keyed on the system alone, that clone would survive a
    reform the system detached for, and NY's decoupled credits would silently
    go on reading pre-reform federal parameters.
    """
    simulation = Simulation(situation=earner_situation())
    policy = simulation.tax_benefit_system
    pinned = get_pre_arpa_eitc_tbs(policy)
    assert get_pre_arpa_eitc_tbs(policy) is pinned

    simulation.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert policy.parameters is not system.parameters
    assert get_pre_arpa_eitc_tbs(policy) is not pinned


@pytest.mark.parametrize("traced", [False, True])
def test_shared_branch_follows_its_parent_whether_or_not_it_is_traced(traced):
    """Tracing gives a simulation its own root node, not its own policy.

    A branch cloned without its own system shares its parent's policy, so the
    detached tree has to reach it however the two roots are spelled. Matching
    on root identity missed every traced branch, and the model's own formulas
    branch this way - itemizing against not itemizing, the state EITC
    refundability branches, marginal tax rates - so a traced simulation
    reported pre-reform numbers under a reform.
    """
    simulation = Simulation(situation=earner_situation())
    simulation.trace = traced
    branch = simulation.get_branch("shared_policy")

    simulation.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert simulation.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX
    assert branch.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX
    assert branch.tax_benefit_system.parameters.children is (
        simulation.tax_benefit_system.parameters.children
    )


def test_traced_simulation_sees_a_later_parameter_reform():
    """A traced root must not outlive the tree its children belong to.

    A shallow root copy keeps the original's children, and each child's parent
    still points at the original root, so a parameter edit clears that root's
    at-instant cache and leaves the traced copy serving pre-reform values.
    """
    simulation = Simulation(
        situation=earner_situation(),
        reform=Reform.from_dict({SINGLE_STANDARD_DEDUCTION: {"2024": 20_000}}),
    )
    simulation.trace = True
    assert simulation.calculate("standard_deduction", 2024)[0] == 20_000

    simulation.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert simulation.calculate("standard_deduction", 2024)[0] == 100_000


def test_lending_a_detached_tree_stops_the_lender_writing_to_it():
    """Owning a tree once is not owning it forever.

    A simulation that detached a private tree, and then lent it to a second
    simulation, has to clone again before its next reform: the borrower can
    see everything it writes.
    """
    lender = Simulation(situation=earner_situation())
    lender.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})
    borrower = Simulation(
        tax_benefit_system=lender.tax_benefit_system, situation=earner_situation()
    )
    assert borrower.calculate("standard_deduction", 2024)[0] == 100_000

    lender.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 7_777}})

    assert lender.calculate("standard_deduction", 2024)[0] == 7_777
    borrower._invalidate_all_caches()
    assert borrower.calculate("standard_deduction", 2024)[0] == 100_000


def test_a_branch_reform_does_not_rewrite_its_parents_policy():
    simulation = Simulation(situation=earner_situation())
    branch = simulation.get_branch("reforming_branch")
    simulation.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 50_000}})

    branch.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert branch.calculate("standard_deduction", 2024)[0] == 100_000
    assert simulation.calculate("standard_deduction", 2024)[0] == 50_000


def test_a_tuple_of_variable_only_reforms_keeps_sharing_the_tree():
    """Core recurses into this override for each member of a reform tuple.

    Reading ``parameters`` inside the outer call's armed window would itself
    trip the barrier, so every tuple reform - including the purely structural
    ones - would have paid for a full tree clone.
    """
    simulation = Simulation(situation=earner_situation())
    policy = simulation.tax_benefit_system

    simulation.apply_reform((NeutralizeIncomeTax, AddedInputReform))

    assert simulation.calculate("income_tax", 2024)[0] == 0
    simulation.set_input("clone_only_income", 2024, [123])
    assert simulation.calculate("clone_only_income", 2024)[0] == 123
    assert policy.parameters is system.parameters
    assert policy.shares_parameters


def test_a_clone_keeps_the_copy_on_write_barrier_its_parent_had():
    """A clone owns its tree, but it still must not be written in place.

    ``clone_spm_system`` hands core an ordinary instance to clone through, by
    stripping the barrier class in ``plain_policy_copy``. Core's clone returns
    that ordinary instance, so without putting the barrier back the clone's own
    tree is writable in place - and a branch of the clone, which copies the
    system and so becomes a second reader, rewrites it.
    """
    simulation = Simulation(situation=earner_situation())
    clone = simulation.clone()

    assert clone.tax_benefit_system.shares_parameters is not None

    branch = clone.get_branch("reforming_branch")
    branch.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert branch.calculate("standard_deduction", 2024)[0] == 100_000
    assert clone.calculate("standard_deduction", 2024)[0] == 14_600
    assert simulation.calculate("standard_deduction", 2024)[0] == 14_600


def test_a_reform_on_a_clone_still_reaches_the_clones_own_policy():
    """The barrier must not make a clone's own reform a no-op.

    The clone is the only reader of its tree until something else copies it, so
    its own reform is free to detach and apply; what it must not do is reach
    the simulation it was cloned from.
    """
    simulation = Simulation(situation=earner_situation())
    assert simulation.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX
    clone = simulation.clone()

    clone.apply_reform({SINGLE_STANDARD_DEDUCTION: {"2024": 100_000}})

    assert clone.calculate("standard_deduction", 2024)[0] == 100_000
    assert simulation.calculate("standard_deduction", 2024)[0] == 14_600
    assert (
        system.parameters.gov.irs.deductions.standard.amount.SINGLE("2024-01-01")
        == 14_600
    )


def test_a_branch_variable_reform_is_not_isolated_from_its_parent():
    """Record the boundary of the barrier: it covers parameters, not variables.

    ``SharedParameterPolicy`` guards the parameter tree. A branch created with
    ``clone_system=False`` still shares its parent's ``variables`` dict - core
    hands the branch the same tax-benefit system object
    (``Simulation.clone``: ``new.tax_benefit_system = self.tax_benefit_system``)
    and every variable operation mutates that registry - so a variable-only
    reform on a branch does reach its parent and siblings.

    This is the documented limit of what this module isolates, not an
    endorsement: a caller that wants a variable reform to itself must pass
    ``clone_system=True``, which every such call site in this repository
    already does. The test exists so the limit cannot be mistaken for
    isolation, and so that closing it later is a visible change.
    """
    parent = Simulation(situation=earner_situation())
    child = parent.get_branch("child")
    sibling = parent.get_branch("sibling")
    assert parent.calculate("income_tax", 2024)[0] == BASELINE_INCOME_TAX

    child.apply_reform(NeutralizeIncomeTax)

    assert child.calculate("income_tax", 2024)[0] == 0
    assert parent.tax_benefit_system.variables is child.tax_benefit_system.variables
    for member in (parent, sibling):
        member._invalidate_all_caches()
        assert member.calculate("income_tax", 2024)[0] == 0

    # A branch that asked for its own system keeps the reform to itself.
    independent = Simulation(situation=earner_situation()).get_branch(
        "independent", clone_system=True
    )
    independent.apply_reform(NeutralizeIncomeTax)
    assert (
        Simulation(situation=earner_situation()).calculate("income_tax", 2024)[0]
        == BASELINE_INCOME_TAX
    )
