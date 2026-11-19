"""Reform simulations derive their policy from the built default system.

``CountryTaxBenefitSystem(reform=...)`` loads every parameter and variable
file and runs the whole parameter pipeline again, although only the steps that
follow the pipeline depend on the reform. A reform simulation instead copies
the default system's processed parameters and variables and runs only those
steps (``CountryTaxBenefitSystem.derive_reform_system``). The system it gets
must be the one a full rebuild produces, and deriving it must leave the default
system unchanged.
"""

import dataclasses
import json
import re
from copy import copy

import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import YEAR
from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable

from policyengine_us import Simulation
from policyengine_us.entities import Person
from policyengine_us.spm import SHARED_TREE_MARK
from policyengine_us.system import CountryTaxBenefitSystem, system
from policyengine_us.tools.per_capita_uprating import (
    DERIVED_FROM,
    detached_copy,
    remove_per_capita_series,
    restore_child_order,
    restore_per_capita_series,
)

SINGLE_STANDARD_DEDUCTION = "gov.irs.deductions.standard.amount.SINGLE"
# A single $50,000 earner in 2024, as in test_spm_simulation_isolation.py:
# a $20,000 single standard deduction leaves taxable income of 30,000, so
# 10% of 11,600 + 12% of 18,400 = 3,368.
BASELINE_INCOME_TAX = 4_016
REFORMED_INCOME_TAX = 3_368
REFORMED_STANDARD_DEDUCTION = 20_000
BASELINE_SINGLE_STANDARD_DEDUCTION = 14_600
# Structural reforms are detected from the reformed parameters: this switch
# makes the full rebuild replace ``refundable_ctc``.
CTC_SWITCH = "gov.contrib.ctc.minimum_refundable.in_effect"
# A structural switch whose first dated value is after 2019, detected from a
# start instant before 2024 (see test_reform_backdating.py).
LINEAR_PHASE_OUT_SWITCH = "gov.contrib.ctc.linear_phase_out.in_effect"
LINEAR_PHASE_OUT_START_YEAR = 2019
# A national total that 391 variables uprate by through its per-capita series,
# and the population series that series divides by.
AGI_TOTAL = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
# Built for parameter uprating, so a full rebuild holds it when it applies a
# reform; the default build's last step refreshes it, and a derived system
# restores the earlier version.
AGI_PER_CAPITA = f"{AGI_TOTAL}_per_capita"
POPULATION = "calibration.gov.census.populations.total"
# Fixed values, not scaled ones: the constructor applies a reform twice.
REFORMED_AGI_TOTAL = 3e13
REFORMED_POPULATION = 4e8
# The only variable that uprates by this national total is rental_income, so
# re-pointing it to CPI-U leaves the total's per-capita series unused, and a
# full rebuild never creates the series.
RENTAL_INCOME_TOTAL = "calibration.gov.irs.soi.rental_income"
RENTAL_INCOME_PER_CAPITA = f"{RENTAL_INCOME_TOTAL}_per_capita"
REFORMED_RENTAL_INCOME_TOTAL = 1e12
CPI_U = "gov.bls.cpi.cpi_u"
SENIOR_DEDUCTION_EXTENSION_SWITCH = (
    "gov.contrib.crfb.senior_deduction_extension.applies"
)
# The structural reform adds the senior deduction to this list from 2029.
DEDUCTIONS_IF_ITEMIZING = "gov.irs.deductions.deductions_if_itemizing"


class derived_reform_test_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Income input added only by the derived-reform test reform"
    # A national total: the system must point it at the per-capita series.
    uprating = AGI_TOTAL


class rental_income_uprated_by_prices(Variable):
    # ``update_variable`` registers this under its ``__name__``.
    uprating = CPI_U


rental_income_uprated_by_prices.__name__ = "rental_income"


class rental_income_with_a_formula(Variable):
    # Inherits the national-total uprating that ``rental_income`` declares.
    def formula(person, period, parameters):
        return person("employment_income", period) * 0


rental_income_with_a_formula.__name__ = "rental_income"


class RentalIncomeFormulaReform(Reform):
    def apply(self):
        self.update_variable(rental_income_with_a_formula)


def set_population_from_2031(parameters):
    parameters.get_child(POPULATION).update(
        start="2031-01-01", value=REFORMED_POPULATION
    )
    return parameters


class VariableAndModifierReform(Reform):
    """Reform steps a parameter dictionary does not exercise.

    ``update_variable`` rather than ``add_variable``, because the constructor
    applies a reform twice. The modifier changes the population series, so
    every per-capita series has to be rebuilt from the reformed values.
    """

    def apply(self):
        self.neutralize_variable("snap")
        self.update_variable(derived_reform_test_income)
        self.update_variable(rental_income_uprated_by_prices)
        self.modify_parameters(set_population_from_2031)


# A bracket of a parameter scale (corpus entry targeted-ctc-base-amount-bounded).
# Which ancestors an update to it marks modified depends on the brackets'
# parent links, which a tree loaded from files and its clone must share.
CTC_BASE_BRACKET_AMOUNT = "gov.irs.credits.ctc.amount.base[0].amount"
PARAMETER_REFORM = {
    # Ends before the parameter's later scheduled values.
    SINGLE_STANDARD_DEDUCTION: {"2026-01-01.2028-12-31": REFORMED_STANDARD_DEDUCTION},
    CTC_BASE_BRACKET_AMOUNT: {"2026-01-01.2100-12-31": 3_000},
    CTC_SWITCH: {"2026-01-01.2100-12-31": True},
    AGI_TOTAL: {"2030-01-01": REFORMED_AGI_TOTAL},
    AGI_PER_CAPITA: {"2026-01-01": 50_000.0},
    RENTAL_INCOME_TOTAL: {"2030-01-01": REFORMED_RENTAL_INCOME_TOTAL},
    # Detected within five years of the start instant; the structural reform
    # it selects edits parameters, inside ``_apply_reforms``.
    SENIOR_DEDUCTION_EXTENSION_SWITCH: {"2025-01-01.2100-12-31": True},
}
COMBINED_REFORM = (PARAMETER_REFORM, VariableAndModifierReform)
# Detection looks five years ahead of the start instant, so a switch that ends
# in 2020 is found from 2019 but not from the default start in 2024.
EARLY_SWITCH_REFORM = {
    LINEAR_PHASE_OUT_SWITCH: {f"{LINEAR_PHASE_OUT_START_YEAR}-01-01.2020-12-31": True}
}
EARLY_START_INSTANT = f"{LINEAR_PHASE_OUT_START_YEAR}-01-01"


def earner_situation():
    return {
        "people": {"person": {"age": {2024: 40}, "employment_income": {2024: 50_000}}},
        "households": {
            "household": {"members": ["person"], "county_fips": {2024: "06037"}}
        },
    }


def parameter_state(policy):
    """Every parameter node's type, dated values, metadata, modified flag
    and child order, the root included.

    Values are compared by ``repr``, which is exact for floats and equal for
    NaN. Metadata is serialized, so a later in-place edit of a metadata
    dictionary shows up against a state recorded earlier. A node that was
    never marked has no ``modified`` flag until ``_apply_reforms`` sets every
    flag to False, and nothing reads the flag before then, so a missing flag
    counts as False.
    """
    state = {}
    root = policy.parameters
    for node in [root, *root.get_descendants()]:
        values = getattr(node, "values_list", None)
        children = getattr(node, "children", None)
        state[node.name] = (
            type(node).__name__,
            None
            if values is None
            else [(entry.instant_str, repr(entry.value)) for entry in values],
            json.dumps(node.metadata, sort_keys=True, default=repr),
            getattr(node, "modified", False),
            None if children is None else list(children),
        )
    return state


MODIFIED_FLAG = 3


def without_modified_flags(state):
    return {
        name: node[:MODIFIED_FLAG] + node[MODIFIED_FLAG + 1 :]
        for name, node in state.items()
    }


def root_attributes(policy):
    """The root node's attribute names, and the values of those a traced or
    shared tree sets there."""
    root = policy.parameters
    return (
        sorted(vars(root)),
        getattr(root, SHARED_TREE_MARK, None),
        root.trace,
        root.tracer,
        root.branch_name,
    )


def build_record_state(policy):
    """What the build record holds, by value and by object identity."""
    build = policy._unreformed_build
    return (
        {
            name: id(variable)
            for name, variable in build.variables_before_reforms.items()
        },
        {name: id(variable) for name, variable in build.variables.items()},
        {
            name: (variable.uprating, sorted(variable._explicit_attribute_names))
            for name, variable in build.total_uprated_variables.items()
        },
        build.per_capita_series_added,
        {
            path: (
                [
                    (entry.instant_str, repr(entry.value))
                    for entry in series.values_list
                ],
                json.dumps(series.metadata, sort_keys=True, default=repr),
                series.parent,
            )
            for path, series in build.per_capita_series_replaced.items()
        },
        dict(build.per_capita_parent_child_order),
    )


def has_parameter(policy, name):
    node = policy.parameters
    for part in name.split("."):
        node = getattr(node, "children", {}).get(part)
        if node is None:
            return False
    return True


def qualified_name(function):
    """The formula's module and qualified name, without the loading system.

    Core names the module of each variable file it loads
    ``{id(system)}_{hash(path)}_{file}``, so the same file loaded by two
    systems gets two module names.
    """
    module = re.sub(r"^\d+_", "", function.__module__)
    return f"{module}.{function.__qualname__}"


def variable_state(policy):
    """Each variable's formulas, by qualified name, and the attributes a
    reform or the system's own build steps change."""
    return {
        name: (
            {
                str(start): qualified_name(formula)
                for start, formula in variable.formulas.items()
            },
            variable.uprating,
            repr(variable.adds),
            repr(variable.subtracts),
            repr(variable.defined_for),
            variable.is_neutralized,
            variable.entity.key,
            variable.definition_period,
            variable.value_type,
            repr(variable.default_value),
            variable.label,
        )
        for name, variable in policy.variables.items()
    }


def test_derived_system_from_an_early_start_instant_matches_a_full_rebuild():
    rebuilt = CountryTaxBenefitSystem(
        reform=EARLY_SWITCH_REFORM, start_instant=EARLY_START_INSTANT
    )
    derived = system.derive_reform_system(
        EARLY_SWITCH_REFORM, start_instant=EARLY_START_INSTANT
    )
    derived_variables = variable_state(derived)
    assert derived_variables == variable_state(rebuilt)
    assert parameter_state(derived) == parameter_state(rebuilt)
    # Guard: the switch replaced a formula. Detection from the default start
    # instant would not find it, so detection ran from the early one.
    assert derived_variables != variable_state(system)


@pytest.mark.parametrize(
    "reform, error",
    [
        # A full rebuild re-points the updated variable from the national
        # total it inherits to the per-capita series, which declares
        # ``uprating`` next to the formula.
        (RentalIncomeFormulaReform, "mixes computation modes"),
        # A full rebuild has no per-capita series yet when it applies the
        # reform; the system builds them afterwards.
        (
            {RENTAL_INCOME_PER_CAPITA: {"2026-01-01": 123.0}},
            f"Could not find the parameter {RENTAL_INCOME_PER_CAPITA}",
        ),
    ],
    ids=["formula-on-a-total-uprated-input", "reform-to-a-per-capita-series"],
)
def test_a_reform_a_full_rebuild_rejects_is_rejected_when_derived(reform, error):
    with pytest.raises(ValueError, match=re.escape(error)):
        CountryTaxBenefitSystem(reform=reform)
    with pytest.raises(ValueError, match=re.escape(error)):
        system.derive_reform_system(reform)
    assert system.can_derive_reform_systems()


def test_a_system_built_under_an_empty_reform_cannot_derive_like_a_derived_one():
    # ``Simulation(reform={})`` derives its system, because the reform is not
    # None. A full rebuild under the same reform must match it, so it must not
    # record a build to derive from either.
    assert not system.derive_reform_system({}).can_derive_reform_systems()
    assert not CountryTaxBenefitSystem(reform={}).can_derive_reform_systems()


def test_a_subclass_that_builds_differently_cannot_derive():
    """A subclass whose constructor does more than this class's would lose
    those steps in a derived system, which runs only ``_apply_reforms``."""

    class SystemWithItsOwnConstructor(CountryTaxBenefitSystem):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class SystemWithTheSameConstructor(CountryTaxBenefitSystem):
        pass

    # Shallow copies read the default system's registry and tree, so only the
    # class differs. Building either subclass would take seconds.
    differently_built = copy(system)
    differently_built.__class__ = SystemWithItsOwnConstructor
    assert not differently_built.can_derive_reform_systems()
    same_build = copy(system)
    same_build.__class__ = SystemWithTheSameConstructor
    assert same_build.can_derive_reform_systems()


def test_a_clone_does_not_keep_the_record_of_its_original_build():
    # The record holds the original's variable objects, which a clone
    # replaces, so keeping it would keep them alive with the clone.
    assert system.clone().__dict__.get("_unreformed_build") is None


def test_deriving_a_reform_system_leaves_the_default_system_unchanged():
    parameters_before = parameter_state(system)
    variables_before = dict(system.variables)
    # Derived systems share most variable objects with the default system,
    # so their attributes must not change either.
    variable_attributes_before = variable_state(system)
    # Every later derivation starts from the build record.
    build_record_before = build_record_state(system)
    entities_before = list(system.entities)
    provider_before = system.spm_forecast_provider

    derived = system.derive_reform_system(COMBINED_REFORM)
    # A reform simulation applies the reform to its system again and adds a
    # baseline arm that shares the default system's policy.
    simulation = Simulation(situation=earner_situation(), reform=COMBINED_REFORM)
    simulation.calculate("household_net_income", 2024)
    simulation.baseline.calculate("household_net_income", 2024)

    assert parameter_state(system) == parameters_before
    assert system.variables.keys() == variables_before.keys()
    assert all(
        system.variables[name] is variable
        for name, variable in variables_before.items()
    )
    assert variable_state(system) == variable_attributes_before
    assert build_record_state(system) == build_record_before
    assert system.entities == entities_before
    assert all(entity._tax_benefit_system is system for entity in system.entities)
    assert system.spm_forecast_provider is provider_before
    assert derived.parameters is not system.parameters
    # The default system stays derivable for the next reform simulation.
    assert system.can_derive_reform_systems()


def test_reform_simulation_derives_its_system_instead_of_rebuilding(monkeypatch):
    def refuse_to_rebuild(*args, **kwargs):
        raise AssertionError("A reform simulation rebuilt the tax-benefit system.")

    # The default system's own cache of parameters at an instant, which a
    # derived system must not read or fill.
    default_at_2024 = system.get_parameters_at_instant("2024-01-01")
    monkeypatch.setattr(CountryTaxBenefitSystem, "__init__", refuse_to_rebuild)
    simulation = Simulation(
        situation=earner_situation(),
        reform={
            SINGLE_STANDARD_DEDUCTION: {
                "2024-01-01.2100-12-31": REFORMED_STANDARD_DEDUCTION
            }
        },
    )

    assert isinstance(simulation.tax_benefit_system, CountryTaxBenefitSystem)
    assert simulation.tax_benefit_system.parameters is not system.parameters
    assert simulation.calculate("income_tax", 2024)[0] == REFORMED_INCOME_TAX
    assert simulation.baseline.calculate("income_tax", 2024)[0] == (BASELINE_INCOME_TAX)
    derived_at_2024 = simulation.tax_benefit_system.get_parameters_at_instant(
        "2024-01-01"
    )
    assert derived_at_2024.gov.irs.deductions.standard.amount.SINGLE == (
        REFORMED_STANDARD_DEDUCTION
    )
    assert system.get_parameters_at_instant("2024-01-01") is default_at_2024
    assert default_at_2024.gov.irs.deductions.standard.amount.SINGLE == (
        BASELINE_SINGLE_STANDARD_DEDUCTION
    )


def test_a_node_without_a_modified_flag_does_not_stop_the_check(monkeypatch):
    # A scale added to the tree after construction (add_child, merge,
    # load_extension) has no ``modified`` flag, since only ``_apply_reforms``
    # sets one on every node. Like other unmarked changes it is carried into
    # derived systems (see ``can_derive_reform_systems``); it must not raise.
    scale = system.parameters.get_child("gov.irs.credits.ctc.amount.base")
    monkeypatch.delattr(scale, "modified")
    assert system.can_derive_reform_systems()


def test_a_restored_series_returns_to_its_place_among_its_siblings():
    """Refreshing a series deletes it and adds it again, which moves it to
    the end of its parent's children; a derived tree must put back the
    order the parent had before the refresh. Removing and restoring series
    must also keep the parent's attribute for each child in step, since
    modifiers reach nodes by attribute."""
    series = {
        name: {
            "metadata": {DERIVED_FROM: f"totals.{name.removesuffix('_per_capita')}"},
            "values": {"2024-01-01": 1.0},
        }
        for name in ("a_per_capita", "b_per_capita")
    }
    tree = ParameterNode("", data={"totals": series})
    totals = tree.get_child("totals")
    order_before = list(totals.children)
    earlier = detached_copy(totals.children["a_per_capita"])
    # What ``add_per_capita_uprating`` does when it refreshes a series.
    refreshed = detached_copy(earlier)
    del totals.children["a_per_capita"]
    totals.add_child("a_per_capita", refreshed)
    assert list(totals.children) != order_before

    restore_per_capita_series(tree, "totals.a_per_capita", earlier)
    restore_child_order(tree, "totals", order_before)

    assert list(totals.children) == order_before
    assert totals.children["a_per_capita"] is earlier
    assert totals.a_per_capita is earlier
    assert earlier.parent is totals
    assert refreshed.parent is None

    removed = totals.children["b_per_capita"]
    remove_per_capita_series(tree, "totals.b_per_capita")
    assert "b_per_capita" not in totals.children
    assert "b_per_capita" not in vars(totals)
    assert removed.parent is None


def test_changed_nodes_holding_per_capita_series_are_rebuilt(monkeypatch):
    """Derivation removes the series the build added and restores those it
    refreshed, which needs those nodes as the build left them. If they have
    changed, without anything marked modified, the system is rebuilt rather
    than derivation failing."""
    refreshed_series = system.parameters.get_child(AGI_PER_CAPITA)
    holder = refreshed_series.parent
    added_series_name = RENTAL_INCOME_PER_CAPITA.rpartition(".")[2]
    added_series_holder = system.parameters.get_child(RENTAL_INCOME_PER_CAPITA).parent
    not_derived = detached_copy(refreshed_series)
    not_derived.metadata = {}
    changes = [
        lambda: monkeypatch.setitem(
            holder.children, "added_after_construction", detached_copy(refreshed_series)
        ),
        lambda: monkeypatch.delitem(
            holder.children, "adjusted_gross_income_per_capita"
        ),
        lambda: monkeypatch.setitem(
            holder.children, "adjusted_gross_income_per_capita", not_derived
        ),
        lambda: monkeypatch.delitem(added_series_holder.children, added_series_name),
    ]
    for change in changes:
        change()
        assert not system.can_derive_reform_systems()
        monkeypatch.undo()
        assert system.can_derive_reform_systems()


def test_a_derived_tree_puts_back_the_recorded_order_of_refreshed_siblings(
    monkeypatch,
):
    """In the current tree each refreshed series is already the last of its
    siblings, so the recorded and final orders agree. Reversing the recorded
    order shows that derivation applies it before the reform steps start."""
    build = system._unreformed_build
    reversed_orders = {
        parent_path: tuple(reversed(order))
        for parent_path, order in build.per_capita_parent_child_order.items()
    }
    assert reversed_orders
    monkeypatch.setattr(
        system,
        "_unreformed_build",
        dataclasses.replace(build, per_capita_parent_child_order=reversed_orders),
    )
    orders_at_start = {}
    apply_reforms = CountryTaxBenefitSystem._apply_reforms

    def recording_apply_reforms(policy, reform, start_instant):
        orders_at_start.update(
            (path, tuple(policy.parameters.get_child(path).children))
            for path in reversed_orders
        )
        apply_reforms(policy, reform, start_instant)

    monkeypatch.setattr(
        CountryTaxBenefitSystem, "_apply_reforms", recording_apply_reforms
    )
    system.derive_reform_system({})
    assert orders_at_start == reversed_orders


def test_a_default_system_of_another_class_is_rebuilt(monkeypatch):
    """A simulation derives only from a default system of the class it would
    build, since another class may build differently."""

    class SystemWithTheSameConstructor(CountryTaxBenefitSystem):
        pass

    other_class = copy(system)
    other_class.__class__ = SystemWithTheSameConstructor
    # Guard: the system itself could derive; only its class differs.
    assert other_class.can_derive_reform_systems()
    built = []

    def record_rebuild(self, **kwargs):
        built.append(kwargs)

    monkeypatch.setattr(CountryTaxBenefitSystem, "__init__", record_rebuild)
    simulation = Simulation.__new__(Simulation)
    simulation.default_tax_benefit_system_instance = other_class

    chosen = simulation._reform_system(PARAMETER_REFORM, None, "2024-01-01")

    assert type(chosen) is CountryTaxBenefitSystem
    assert built == [
        {"reform": PARAMETER_REFORM, "spm": None, "start_instant": "2024-01-01"}
    ]


def test_a_changed_default_system_is_rebuilt_rather_than_derived(monkeypatch):
    """A default system changed after it was built is rebuilt from files.

    A full rebuild never saw the change, so a derived system would differ
    from it.
    """
    changed_variables = dict(system.variables)
    changed_variables["snap"] = system.variables["income_tax"]
    monkeypatch.setattr(system, "variables", changed_variables)
    assert not system.can_derive_reform_systems()
    monkeypatch.undo()
    assert system.can_derive_reform_systems()

    # A variable added to the registry, as ``load_extension`` adds them.
    monkeypatch.setitem(
        system.variables, "added_after_construction", system.variables["income_tax"]
    )
    assert not system.can_derive_reform_systems()
    monkeypatch.undo()
    assert system.can_derive_reform_systems()

    standard_deduction = system.parameters.get_child(SINGLE_STANDARD_DEDUCTION)
    monkeypatch.setattr(standard_deduction, "modified", True)
    assert not system.can_derive_reform_systems()
    monkeypatch.undo()
    assert system.can_derive_reform_systems()


def test_simulation_rebuilds_when_its_default_system_cannot_derive(monkeypatch):
    built = []

    def record_rebuild(self, **kwargs):
        # Records the arguments instead of building, which takes seconds.
        built.append(kwargs)

    monkeypatch.setattr(CountryTaxBenefitSystem, "__init__", record_rebuild)
    monkeypatch.setattr(
        CountryTaxBenefitSystem, "can_derive_reform_systems", lambda self: False
    )
    config = {"geography_kind": "national"}

    chosen = Simulation.__new__(Simulation)._reform_system(
        PARAMETER_REFORM, config, EARLY_START_INSTANT
    )

    assert type(chosen) is CountryTaxBenefitSystem
    assert built == [
        {
            "reform": PARAMETER_REFORM,
            "spm": config,
            "start_instant": EARLY_START_INSTANT,
        }
    ]


# The tests that share this fixture come last, so that its two systems are
# not kept alive while the tests above build their own.
@pytest.fixture(scope="module")
def combined_systems():
    """A full rebuild and a derived system under the same combined reform.

    Also records each system's policy as ``_apply_reforms`` starts, where
    the steps that depend on the reform begin.
    """
    policy_when_reforms_start = {}
    apply_reforms = CountryTaxBenefitSystem._apply_reforms

    def recording_apply_reforms(policy, reform, start_instant):
        policy_when_reforms_start[id(policy)] = (
            parameter_state(policy),
            variable_state(policy),
        )
        apply_reforms(policy, reform, start_instant)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            CountryTaxBenefitSystem, "_apply_reforms", recording_apply_reforms
        )
        rebuilt = CountryTaxBenefitSystem(reform=COMBINED_REFORM)
        # What sharing and a traced request leave on the default tree's root,
        # which a tree loaded from files does not have.
        root = system.parameters
        patch.setattr(root, SHARED_TREE_MARK, True, raising=False)
        patch.setattr(root, "trace", True)
        patch.setattr(root, "tracer", object())
        patch.setattr(root, "branch_name", "a branch")
        derived = system.derive_reform_system(COMBINED_REFORM)
    return (
        rebuilt,
        derived,
        policy_when_reforms_start[id(rebuilt)],
        policy_when_reforms_start[id(derived)],
    )


def test_a_derived_system_starts_the_reform_steps_from_the_same_policy(
    combined_systems,
):
    """Everything construction does before ``_apply_reforms`` is independent
    of the reform, so a derived system must reach that point holding what a
    full rebuild holds there, not what the default system holds afterwards."""
    _, _, rebuilt_at_start, derived_at_start = combined_systems
    # Without the ``modified`` flags: the parameter pipeline leaves many set,
    # nothing reads them during construction, and ``_apply_reforms`` clears
    # them all before it applies the reform that sets the final ones (which
    # the other tests compare).
    rebuilt_parameters, rebuilt_variables = rebuilt_at_start
    derived_parameters, derived_variables = derived_at_start
    for rebuilt_state, derived_state in (
        (
            without_modified_flags(rebuilt_parameters),
            without_modified_flags(derived_parameters),
        ),
        (rebuilt_variables, derived_variables),
    ):
        differing_names = sorted(
            name
            for name in rebuilt_state.keys() | derived_state.keys()
            if rebuilt_state.get(name) != derived_state.get(name)
        )
        assert differing_names == []


def test_derived_parameters_match_a_full_rebuild(combined_systems):
    rebuilt, derived, *_ = combined_systems
    rebuilt_parameters = parameter_state(rebuilt)
    derived_parameters = parameter_state(derived)
    assert derived_parameters == rebuilt_parameters
    assert root_attributes(derived) == root_attributes(rebuilt)
    # Guards: the default system builds the per-capita series that the
    # re-pointed variable no longer uses; the full rebuild does not. The
    # structural reform's parameter edit took effect. The bracket update
    # marked the bracket modified.
    assert has_parameter(system, RENTAL_INCOME_PER_CAPITA)
    assert RENTAL_INCOME_PER_CAPITA not in rebuilt_parameters
    deductions_in_2029 = [
        policy.parameters.get_child(DEDUCTIONS_IF_ITEMIZING)("2029-01-01")
        for policy in (derived, system)
    ]
    assert deductions_in_2029[0] != deductions_in_2029[1]
    assert derived_parameters[CTC_BASE_BRACKET_AMOUNT][MODIFIED_FLAG]


def test_derived_variables_match_a_full_rebuild(combined_systems):
    rebuilt, derived, *_ = combined_systems
    derived_variables = variable_state(derived)
    assert derived_variables == variable_state(rebuilt)
    # Guards: each reform step the comparison covers took effect.
    assert derived_variables["snap"][5]
    assert derived_variables["derived_reform_test_income"][1] == (
        f"{AGI_TOTAL}_per_capita"
    )
    assert (
        variable_state(system)["refundable_ctc"][0]
        != (derived_variables["refundable_ctc"][0])
    )


def test_derived_system_is_a_country_system_like_a_full_rebuild(combined_systems):
    rebuilt, derived, *_ = combined_systems
    # Class attributes such as ``auto_carry_over_input_variables`` and methods
    # such as ``clone`` come from the class, which core's ``Reform`` replaces.
    assert type(derived) is type(rebuilt) is CountryTaxBenefitSystem
    assert derived._per_capita_uprating_built
    for entity in derived.entities:
        assert entity._tax_benefit_system is derived
    assert derived.person_entity in derived.entities
    assert all(entity in derived.entities for entity in derived.group_entities)
    assert derived.spm_forecast_provider is not system.spm_forecast_provider
    assert derived.modelled_policies == rebuilt.modelled_policies
    assert derived.modelled_policies is not system.modelled_policies
    assert derived.variable_module_metadata == rebuilt.variable_module_metadata
    assert derived.variable_module_metadata is not system.variable_module_metadata


def test_a_derived_system_cannot_derive_another(combined_systems):
    rebuilt, derived, *_ = combined_systems
    assert not rebuilt.can_derive_reform_systems()
    assert not derived.can_derive_reform_systems()
    with pytest.raises(ValueError, match="built without a reform"):
        derived.derive_reform_system(EARLY_SWITCH_REFORM)
