"""Small storage backend for the Social Security input state machine.

The country is intentionally never imported. Core's installed source bodies
implement every write, builder, copy, replay, extraction and dump route below;
the US module's complete function bodies implement the hooks. Entity and
variable descriptors, dataset construction, and disk dump bytes are synthetic.
Periods, memory storage, store history, sequence numbers, dependency drops,
eviction and period helpers use Core itself. This tests input semantics and
Core's source selection, not country benefit formulas or full-model performance. A reported -> base -> public formula chain exercises
cache invalidation and scored-year factors. The synthetic uprating index
doubles each year so source changes have exact reader values.

Remaining Core substitutions are limited to fixture plumbing:
- Holder.__init__ and default_array construct one-person float arrays in
  memory; create_disk_storage supplies the JSON-backed Disk used only by
  dump/restore.
- Population construction, get_holder and clone provide one person and one
  household. System descriptors and parameters replace country legislation.
- Simulation.__init__, build_from_populations, get_holder and
  get_variable_population attach those populations. calculate provides its
  single-thread fast-cache entry point, _run_formula defines the tiny
  reported/base/public chain, _cast_formula_result converts float arrays,
  _check_period_consistency accepts exact annual reads, and _check_for_cycle
  skips tracing for this acyclic chain. check_macro_cache returns False;
  subsample is unsupported because the fixture contains one person.
- Builder entity registration/declaration and membership methods only create
  that one-person situation; _get_person_count and check_type reflect its
  fixed shape. Dataset.load supplies the tiny dictionary input payload.
  get_parameter returns the fixture's doubling uprating index.
- Dumper _dump_entity/_restore_entity/_restore_count replace entity
  serialization only; Disk replaces OnDiskStorage's physical bytes. Public
  dump/restore bodies, holder provenance, memory tiers and source
  restoration remain Core/US code.
"""

from __future__ import annotations

import ast
import copy
import json
import logging
import operator
import os
import sys
import types
import warnings
from contextlib import ExitStack, nullcontext
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache, wraps
from importlib.metadata import distribution
from pathlib import Path
from unittest.mock import patch
from weakref import WeakKeyDictionary, ref

import numpy as np
from policyengine_core import commons, periods
from policyengine_core.data_storage.in_memory_storage import InMemoryStorage
from policyengine_core.data_storage.store_history import (
    StoreHistory,
    _period_from_storage_key,
    advance_sequence_past,
    next_sequence_number,
)
from policyengine_core.periods import Period
from policyengine_core.simulations import simulation as core_simulation


as_period = periods.period


ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)


@lru_cache(maxsize=None)
def source_tree(source):
    return ast.parse(source.read_text())


@lru_cache(maxsize=None)
def compiled_nodes(source, names, class_name=None):
    """Cache code, never live functions or their mutable fixture namespaces."""
    tree = source_tree(source)
    if class_name:
        tree = next(
            n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name
        )
    nodes = [
        next(
            n
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name
        )
        for name in names
    ]
    future = ast.ImportFrom(
        module="__future__", names=[ast.alias(name="annotations")], level=0
    )
    code = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    return compile(code, str(source), "exec")


def execute(source, names, namespace, class_name=None):
    """Execute selected, unmodified source bodies in a fresh namespace."""
    exec(compiled_nodes(source, tuple(names), class_name), namespace)
    return {name: namespace[name] for name in names}


@lru_cache(maxsize=None)
def compiled_hooks(source):
    tree = source_tree(source)
    body = [
        n
        for n in tree.body
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.ClassDef, ast.FunctionDef))
    ]
    code = ast.fix_missing_locations(
        ast.Module(
            body=[
                ast.ImportFrom(
                    module="__future__", names=[ast.alias(name="annotations")], level=0
                ),
                *body,
            ],
            type_ignores=[],
        )
    )
    return compile(code, str(source), "exec")


class Disk:
    """Tiny on-disk adapter used by unchanged public Core dump functions."""

    def __init__(self, storage_dir, **kwargs):
        self.storage_dir = str(storage_dir)
        self.values = {}
        Path(storage_dir).mkdir(exist_ok=True)

    def put(self, value, period):
        Path(self.storage_dir, f"default_{period}.npy").write_text(
            json.dumps(np.asarray(value).tolist())
        )

    def restore(self):
        self.values = {
            as_period(path.stem.removeprefix("default_")): np.array(
                json.loads(path.read_text())
            )
            for path in Path(self.storage_dir).glob("*.npy")
        }

    def get_known_periods(self):
        return list(self.values)

    def get(self, period):
        return self.values[as_period(period)]


class Backend:
    """Install the unchanged hooks around unchanged Core routes in isolation."""

    def __init__(self, *, cache_blacklist=(), variables_to_drop=()):
        self.stack = ExitStack()
        self.cache_blacklist = tuple(cache_blacklist)
        self.variables_to_drop = tuple(variables_to_drop)
        try:
            self._setup()
        except BaseException:
            self.stack.close()
            raise

    def _setup(self):
        cache_blacklist = self.cache_blacklist
        variables_to_drop = self.variables_to_drop
        core = Path(distribution("policyengine-core").locate_file("policyengine_core"))
        calculation_frames = core_simulation._calculation_frames
        formula_simulation = core_simulation._formula_simulation
        branch_clone = core_simulation._branch_clone
        BranchClone = core_simulation._BranchClone

        person = types.SimpleNamespace(key="person", plural="people", is_person=True)
        member = types.SimpleNamespace(
            key="member", plural="members", max=None, subroles=None
        )
        household = types.SimpleNamespace(
            key="household",
            plural="households",
            is_person=False,
            roles=(member,),
            flattened_roles=(member,),
        )

        class Holder:
            def __init__(self, population, name):
                self.population = population
                self.simulation = population.simulation
                self.variable = self.simulation.tax_benefit_system.get_variable(name)
                self._memory_storage = InMemoryStorage(is_eternal=False)
                self._disk_storage = None
                self._on_disk_storable = False
                self._do_not_store = name in (
                    self.simulation.memory_config.variables_to_drop
                )

            def _storage_period(self, period):
                return as_period(period)

            def default_array(self):
                return np.zeros(1)

            def _get_array_from_storage(self, period, branch_name="default"):
                return self._memory_storage.get(period, branch_name)

            def get_array(self, period, branch_name="default"):
                branch = self._branch_storing(period, branch_name)
                return (
                    None
                    if branch is None
                    else self._get_array_from_storage(period, branch)
                )

            def get_known_periods(self):
                return list(
                    dict.fromkeys(
                        p for _, p in self._memory_storage.get_known_branch_periods()
                    )
                )

            def create_disk_storage(self, directory, preserve=True):
                return Disk(Path(directory) / self.variable.name)

        class Population:
            def __init__(self, entity, simulation=None):
                self.entity = entity
                self.simulation = simulation
                self._holders = {}
                self.count = 1
                self.ids = np.array([1])
                self.members_entity_id = np.array([0])

            def get_holder(self, name):
                if not self.entity.is_person:
                    raise ValueError("All fixture variables belong to people")
                if name not in self._holders:
                    self._holders[name] = Holder(self, name)
                return self._holders[name]

            def clone(self, simulation, *args, **kwargs):
                clone = Population(self.entity, simulation)
                clone._holders = {
                    name: holder.clone(clone, **kwargs)
                    for name, holder in self._holders.items()
                }
                return clone

        class System:
            _social_security_input_compatibility = True
            person_entity = person
            group_entities = [household]
            data_modified = False
            auto_carry_over_input_variables = True

            def __init__(self):
                self.cache_blacklist = list(cache_blacklist)
                self.variables = {
                    name: types.SimpleNamespace(
                        name=name,
                        entity=person,
                        definition_period="year",
                        is_neutralized=False,
                        value_type=float,
                        dtype=np.dtype("float64"),
                        set_input=None,
                        end=None,
                        requires_computation_after=None,
                        defined_for=None,
                        uprating="fixture_index",
                        calculate_output=None,
                        quantity_type="flow",
                        check_uprating_value_type=lambda: None,
                        is_input_variable=lambda name=name: (
                            name.endswith("_reported")
                            or name
                            in (
                                "independent_input",
                                "raw_seed",
                                "early_derived",
                                "late_derived",
                            )
                        ),
                    )
                    for name in (
                        "independent_input",
                        "raw_seed",
                        "early_derived",
                        "late_derived",
                        "unrelated_formula",
                        *COMPONENTS,
                        *(f"{name}_reported" for name in COMPONENTS),
                        *(f"{name}_base" for name in COMPONENTS),
                    )
                }

            def instantiate_entities(self):
                return {
                    entity.key: Population(entity) for entity in (person, household)
                }

            def get_variable(self, name, **kwargs):
                return self.variables[name]

            def entities_plural(self):
                return ["people", "households"]

            def clone(self):
                return self

            def parameters(self, *args):
                return types.SimpleNamespace(gov=types.SimpleNamespace(abolitions={}))

        system = System()

        class Simulation:
            _open_frames = None
            default_role = "member"
            default_input_period = "2024"
            default_calculation_period = "2024"

            def __init__(self, tax_benefit_system=None, populations=None, **kwargs):
                self.tax_benefit_system = tax_benefit_system or system
                self._user_input_keys = set()
                self._user_input_contexts = []
                self._inputs_set = 0
                self._input_epoch = 0
                self._store_history = None
                self._requested_variables = None
                self._calculations_started = 0
                self._calculations_in_flight = 0
                self.input_variables = []
                self.parent_branch = None
                self.branch_name = "default"
                self.branches = {}
                self._data_storage_dir = None
                self._storage_dir_parent = None
                self.invalidated_caches = set()
                self._fast_cache = {}
                self.start_instant = None
                self.opt_out_cache = bool(cache_blacklist)
                self.memory_config = types.SimpleNamespace(
                    variables_to_drop=set(variables_to_drop),
                    priority_variables=set(self.tax_benefit_system.variables),
                )
                self.trace = False
                self.fail_after_store = False
                self.build_from_populations(
                    populations or self.tax_benefit_system.instantiate_entities()
                )
                if kwargs.get("situation") is not None:
                    # Country constructor plumbing uses the same actual Core
                    # builder; no input migration logic lives in this fixture.
                    Builder().build_from_dict(
                        self.tax_benefit_system, kwargs["situation"], simulation=self
                    )

            def build_from_populations(self, populations):
                self.populations = populations
                self.persons = populations["person"]
                for population in populations.values():
                    population.simulation = self

            def get_holder(self, name):
                return self.persons.get_holder(name)

            def get_variable_population(self, name):
                return self.persons

            def subsample(self, *args):
                raise NotImplementedError(
                    "Dataset subsampling is outside this storage backend"
                )

            def calculate(self, name, period):
                # The country-free fixture has no tracer or concurrent
                # formulas. Retain Core's public reader cache behavior while
                # its installed _calculate body supplies the actual value.
                period = as_period(period)
                key = (name, period)
                if key not in self._fast_cache:
                    self._fast_cache[key] = self._calculate(name, period)
                return self._fast_cache[key]

            def _calculate(self, name, period):
                raise AssertionError("Installed Core calculation body was not loaded")

            def check_macro_cache(self, *args):
                return False

            def _check_period_consistency(self, period, variable):
                if period.unit != "year" or period.size != 1:
                    raise ValueError("A compound reader requires an exact source")

            def _check_for_cycle(self, *args):
                pass

            def _run_formula(self, variable, population, period):
                if variable.name == "unrelated_formula":
                    return np.array([77.0])
                if variable.name in COMPONENTS:
                    return self.calculate(f"{variable.name}_base", period) * 2
                if variable.name.endswith("_base"):
                    component = variable.name.removesuffix("_base")
                    return self.calculate(f"{component}_reported", period)
                return None

            def _cast_formula_result(self, array, variable):
                return np.asarray(array, dtype=float)

        class DelegatingSimulation(Simulation):
            def set_input(self, name, period, value):
                super().set_input(name, period, value)
                if self.fail_after_store and name == self.fail_name:
                    self.last_error = RuntimeError(
                        "stored input before intentional setter failure"
                    )
                    raise self.last_error

        class Builder:
            default_period = None

            def __init__(self):
                self.input_buffer = {}
                self.entity_counts = {}
                self.memberships = {}

            def explicit_singular_entities(self, system, values):
                return values

            def register_variable(self, *args):
                pass

            def add_person_entity(self, entity, values):
                self.persons_plural = entity.plural
                for inputs in values.values():
                    for name, dated in inputs.items():
                        self.input_buffer[name] = {
                            str(period): [amount] for period, amount in dated.items()
                        }
                return list(values)

            def add_group_entity(self, *args):
                pass

            def add_default_group_entity(self, *args):
                pass

            def declare_person_entity(self, key, ids):
                self.populations[key].ids = np.asarray(ids)

            def declare_entity(self, key, ids):
                self.populations[key].ids = np.asarray(ids)

            def join_with_persons(self, *args):
                pass

        class Dataset:
            FLAT_FILE = "flat"
            TIME_PERIOD_ARRAYS = "period_arrays"
            data_format = TIME_PERIOD_ARRAYS
            time_period = "2024"

            def __init__(self, values):
                self.values = values

            def load(self):
                return {
                    "person_id": {"2024": [1]},
                    "household_id": {"2024": [1]},
                    "person_household_id": {"2024": [1]},
                    **self.values,
                }

        namespace = dict(
            __name__="policyengine_core.holders.holder",
            __package__="policyengine_core.holders",
            np=np,
            numpy=np,
            periods=periods,
            Period=Period,
            os=os,
            warnings=warnings,
            types=types,
            json=json,
            logging=logging,
            log=logging.getLogger(__name__),
            commons=commons,
            next_sequence_number=next_sequence_number,
            _calculation_frames=calculation_frames,
            _formula_simulation=formula_simulation,
            _branch_clone=branch_clone,
            _BranchClone=BranchClone,
            _note_unobserved_activity=core_simulation._note_unobserved_activity,
            _taint_waiting_frames=core_simulation._taint_waiting_frames,
            _frame_for=core_simulation._frame_for,
            _RERUNS_AFTER_INPUT_CHANGE=core_simulation._RERUNS_AFTER_INPUT_CHANGE,
            nullcontext=nullcontext,
            directory_containing=lambda path: None,
            PreservedUserInput=core_simulation.PreservedUserInput,
            StoreHistory=StoreHistory,
            NpEncoder=core_simulation.NpEncoder,
            ETERNITY="eternity",
            YEAR="year",
            MONTH="month",
            QuantityType=types.SimpleNamespace(STOCK="stock"),
            Enum=Enum,
            SpiralError=type("SpiralError", (Exception,), {}),
            FullTracer=type("FullTracer", (), {}),
            get_parameter=lambda *args: lambda instant: 2 ** (instant.year - 2023),
            Dataset=Dataset,
            Simulation=Simulation,
            SimulationBuilder=Builder,
            _get_person_count=lambda values: 1,
            check_type=lambda *args: None,
            PeriodMismatchError=ValueError,
            _period_from_storage_key=_period_from_storage_key,
            copy=copy,
            # Core 3.33.13's build_default_simulation checks its count with
            # operator.index.
            operator=operator,
        )
        holder_methods = (
            "clone",
            "_get_array_from_storage",
            "get_array",
            "get_known_periods",
            "get_known_branch_periods",
            "set_input",
            "_set",
            "_to_array",
            "_raise_if_input_contains_nan",
            "_record_store",
            "_record_inputs",
            "_evict_fast_cache",
            "_input_unchanged",
            "_is_input",
            "_has_unnumbered_values",
            "_stored_sequence_number",
            "_storage_period",
            "_stores",
            "put_in_cache",
            "_seed_input_storage",
            "_record_input_storage",
            "_stores_user_input",
            "_readable_branches",
            "_branch_storing",
            "is_derived",
            "get_input_periods",
            "_drop_computed",
            "delete_arrays",
            "_stored_keys",
            "_forget_deleted_inputs",
        )
        for name, method in execute(
            core / "holders/holder.py", holder_methods, namespace, "Holder"
        ).items():
            setattr(Holder, name, method)
        helper_source = core / "holders/helpers.py"
        # Later compatible Core releases add helper calls to these routes.
        # Execute the installed helper bodies together so their internal
        # dependencies remain the real implementation across Core versions.
        helper_names = tuple(
            node.name
            for node in source_tree(helper_source).body
            if isinstance(node, ast.FunctionDef)
        )
        helpers = types.ModuleType("policyengine_core.holders.helpers")
        helpers.__dict__.update(namespace)
        helpers.__dict__["__name__"] = helpers.__name__
        helpers.__dict__["__package__"] = "policyengine_core.holders"
        core_helpers = execute(helper_source, helper_names, helpers.__dict__)
        namespace.update(core_helpers)
        # Variable supplies this default handler for yearly FLOW variables.
        for variable in system.variables.values():
            variable.set_input = core_helpers["set_input_divide_by_period"]
        # Core 3.33.12 cleans overlapping raw seeds after a direct set_input;
        # 3.33.2 does this only in dispatch/divide helpers. Keep the reference
        # model tied to the installed behavior rather than a version string.
        self.cleans_raw_overlaps = "_drop_calculated_over_own_period" in core_helpers
        simulation_source = core / "simulations/simulation.py"
        # _latest_input_key calls _end_order, which uses Core's calendar
        # table even for yearly sources. Load that literal from the same
        # installed module rather than maintaining a second calendar table.
        day_offsets = next(
            node.value
            for node in source_tree(simulation_source).body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "_DAYS_BEFORE_MONTH"
                for target in node.targets
            )
        )
        namespace["_DAYS_BEFORE_MONTH"] = ast.literal_eval(day_offsets)
        execute(
            simulation_source,
            ("_end_order", "_latest_input_key", "_uprating_index_value"),
            namespace,
        )
        sim_methods = (
            "set_input",
            "delete_arrays",
            "_get_store_history",
            "_get_requested_variables",
            "_drop_values_that_may_depend_on",
            "build_from_dataset",
            "clone",
            "get_branch",
            "apply_reform",
            "_invalidate_all_caches",
            "drop_computed_arrays",
            "extract_person",
            "_get_visible_branch_names",
            "_get_set_input_periods",
            "_get_recorded_input_array",
            "_calculate",
            "calculate_add",
            "_cache_option_result",
            "_calculation_start",
            "_cache_result",
            "_may_keep",
            "_input_set_meanwhile",
            "_drop_computed",
        )
        for name, method in execute(
            core / "simulations/simulation.py", sim_methods, namespace, "Simulation"
        ).items():
            setattr(Simulation, name, method)
        builder_methods = (
            "build_default_simulation",
            "build_from_variables",
            "build_from_dict",
            "build_from_entities",
            "finalize_variables_init",
        )
        for name, method in execute(
            core / "simulations/simulation_builder.py",
            builder_methods,
            namespace,
            "SimulationBuilder",
        ).items():
            setattr(Builder, name, method)

        def module(name, **values):
            result = types.ModuleType(name)
            result.__dict__.update(values)
            return result

        dumper = module(
            "policyengine_core.tools.simulation_dumper",
            os=os,
            warnings=warnings,
            Simulation=Simulation,
            OnDiskStorage=Disk,
            ETERNITY="eternity",
            next_sequence_number=next_sequence_number,
            DERIVED_PERIODS_FILE="derived_periods.txt",
            DUMP_FORMAT_FILE="dump_format.txt",
            DUMP_FORMAT_VERSION=1,
            _dump_entity=lambda *args: None,
            _restore_entity=lambda *args: 1,
            # From Core 3.33.13 restore_simulation also restores each
            # population's count; the fixture's one-person populations keep
            # theirs.
            _restore_count=lambda *args: None,
        )
        execute(
            core / "tools/simulation_dumper.py",
            (
                "dump_simulation",
                "restore_simulation",
                "_dump_holder",
                "_restore_holder",
                "_restore_input",
            ),
            dumper.__dict__,
        )
        period_hooks = module(
            "policyengine_us.tools.social_security_periods",
            np=np,
            YEAR="year",
            CoreSimulation=Simulation,
            SOCIAL_SECURITY_COMPONENTS=COMPONENTS,
            wraps=wraps,
        )
        enums = execute(
            ROOT / "tools/social_security_benefit_levers.py",
            ("SocialSecurityBenefitSource", "SocialSecurityFund"),
            {"Enum": Enum, "__name__": __name__},
        )
        period_hooks.__dict__.update(enums)
        execute(
            ROOT / "tools/social_security_periods.py",
            (
                "install_social_security_period_compatibility",
                "_calculate_social_security_period",
            ),
            period_hooks.__dict__,
        )
        modules = {
            "policyengine_core": module("policyengine_core"),
            "policyengine_core.holders": module(
                "policyengine_core.holders", Holder=Holder
            ),
            "policyengine_core.holders.helpers": helpers,
            "policyengine_core.simulations": module(
                "policyengine_core.simulations", Simulation=Simulation
            ),
            "policyengine_core.simulations.simulation": module(
                "policyengine_core.simulations.simulation",
                _note_input_change=core_simulation._note_input_change,
                _calculation_frames=calculation_frames,
                _taint_waiting_frames=namespace["_taint_waiting_frames"],
                NpEncoder=core_simulation.NpEncoder,
            ),
            "policyengine_core.simulations.simulation_builder": module(
                "policyengine_core.simulations.simulation_builder",
                SimulationBuilder=Builder,
            ),
            "policyengine_core.tools": module(
                "policyengine_core.tools", simulation_dumper=dumper
            ),
            "policyengine_core.tools.simulation_dumper": dumper,
            "policyengine_us": module("policyengine_us", Simulation=Simulation),
            "policyengine_us.tools": module("policyengine_us.tools"),
            "policyengine_us.tools.social_security_periods": period_hooks,
        }
        self.stack.enter_context(patch.dict(sys.modules, modules))
        # Mutation evidence may supply a separate, minimally reverted source
        # copy; normal tests always execute the actual production module.
        hook_source = Path(
            os.environ.get(
                "SOCIAL_SECURITY_INPUT_SOURCE", ROOT / "tools/social_security_inputs.py"
            )
        )
        hook_module = module(
            "_social_security_state_hooks",
            json=json,
            ContextVar=ContextVar,
            WeakKeyDictionary=WeakKeyDictionary,
            advance_sequence_past=advance_sequence_past,
            ref=ref,
            dataclass=dataclass,
            wraps=wraps,
            Path=Path,
            next_sequence_number=next_sequence_number,
            get_stored_input=namespace["get_stored_input"],
            to_period=as_period,
            NpEncoder=core_simulation.NpEncoder,
            ETERNITY="eternity",
        )
        self.stack.enter_context(
            patch.dict(sys.modules, {hook_module.__name__: hook_module})
        )
        hook_namespace = hook_module.__dict__
        execute(
            ROOT / "tools/period_branch.py", ("delete_input_values",), hook_namespace
        )
        # Keep every assignment, class and function from the real hook module;
        # execute anew for each example so all mutable state stays private.
        exec(compiled_hooks(hook_source), hook_namespace)
        hook_namespace["install_social_security_input_compatibility"]()
        self.Simulation = Simulation
        self.DelegatingSimulation = DelegatingSimulation
        self.Builder = Builder
        self.Dataset = Dataset
        self.system = system
        self.hooks = hook_namespace
        self.dumper = dumper
        self.helpers = helpers
        self.next_sequence_number = next_sequence_number

    def close(self):
        self.stack.close()
