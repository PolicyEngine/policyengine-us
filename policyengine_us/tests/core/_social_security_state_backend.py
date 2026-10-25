"""Small storage backend for the Social Security input state machine.

The country is intentionally never imported. Core's installed source bodies
implement every write, builder, copy, replay, extraction and dump route below;
the US module's complete function bodies implement the hooks. Only entities,
arrays, periods, storage and dependency bookkeeping are synthetic. This tests
input semantics, not benefit calculations or full-model performance.
"""

from __future__ import annotations

import ast
import copy
import itertools
import json
import logging
import os
import sys
import types
import warnings
from contextlib import ExitStack
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache, wraps
from importlib.metadata import distribution
from pathlib import Path
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)


@dataclass(frozen=True, order=True)
class Instant:
    year: int
    month: int = 1

    @property
    def date(self):
        return (self.year, self.month)


@dataclass(frozen=True)
class Period:
    start: Instant
    size: int = 1
    unit: str = "year"

    @property
    def stop(self):
        return Instant(self.start.year + self.size - 1, 12)

    def __str__(self):
        if self.unit == "eternity":
            return "eternity"
        return (
            str(self.start.year)
            if self.size == 1
            else f"year:{self.start.year}:{self.size}"
        )

    def contains(self, other):
        return self.start <= other.start and self.stop >= other.stop


def as_period(value):
    if isinstance(value, Period):
        return value
    if str(value) == "eternity":
        return Period(Instant(0), unit="eternity")
    parts = str(value).split(":")
    return (
        Period(Instant(int(parts[-2])), int(parts[-1]))
        if len(parts) == 3
        else Period(Instant(int(value)))
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
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.FunctionDef))
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


class Storage:
    """Memory arrays plus Core's separate carry-over and input-tier marks."""

    is_eternal = False

    def __init__(self):
        self._arrays = {}
        self._inputs = set()
        self._sequence_numbers = {}

    def get(self, period, branch_name="default"):
        return self._arrays.get(f"{branch_name}:{as_period(period)}")

    def has(self, period, branch_name="default"):
        return f"{branch_name}:{as_period(period)}" in self._arrays

    def is_derived(self, period, branch_name="default"):
        return (
            self.has(period, branch_name)
            and f"{branch_name}:{as_period(period)}" not in self._inputs
        )

    def put(
        self, value, period, branch_name="default", derived=False, sequence_number=None
    ):
        key = f"{branch_name}:{as_period(period)}"
        self._arrays[key] = np.asarray(value).copy()
        self._sequence_numbers[key] = sequence_number
        if derived:
            self._inputs.discard(key)
        else:
            self._inputs.add(key)

    def get_known_branch_periods(self):
        return [
            (key.split(":", 1)[0], as_period(key.split(":", 1)[1]))
            for key in self._arrays
        ]

    def delete(self, period=None, branch_name="default"):
        for key in list(self._arrays):
            branch, when = key.split(":", 1)
            if branch == branch_name and (
                period is None or as_period(period).contains(as_period(when))
            ):
                del self._arrays[key]
        self._unmark_dropped_keys()

    def mark_derived_except(self, kept):
        self._inputs.intersection_update(kept)

    def drop_computed(self, since=None):
        dropped = [
            key
            for key in self._arrays
            if key not in self._inputs
            and (since is None or (self._sequence_numbers.get(key) or 0) >= since)
        ]
        for key in dropped:
            del self._arrays[key]
        self._unmark_dropped_keys()
        return len(dropped)

    def _unmark_dropped_keys(self):
        self._inputs.intersection_update(self._arrays)

    def _stop_sharing_dropped_keys(self):
        pass

    def _forget_dropped_numbers(self):
        self._sequence_numbers = {
            key: number
            for key, number in self._sequence_numbers.items()
            if key in self._arrays
        }

    def clone(self, **kwargs):
        return copy.deepcopy(self)


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


class History:
    def copy(self):
        return History()

    def record_unknown_sources(self, *args):
        pass


class Backend:
    """Install the unchanged hooks around unchanged Core routes in isolation."""

    def __init__(self):
        self.stack = ExitStack()
        try:
            self._setup()
        except BaseException:
            self.stack.close()
            raise

    def _setup(self):
        core = Path(distribution("policyengine-core").locate_file("policyengine_core"))
        counter = itertools.count(1)

        def next_sequence():
            return next(counter)

        periods = types.SimpleNamespace(
            period=as_period,
            YEAR="year",
            MONTH="month",
            ETERNITY="eternity",
            key_period_size=lambda p: p.size,
        )
        commons = types.SimpleNamespace(
            empty_clone=lambda value: object.__new__(type(value))
        )
        calculation_frames = ContextVar("state_machine_frames", default=())
        branch_clone = ContextVar("state_machine_branch_clone", default=None)

        class BranchClone:
            def __init__(self, simulation):
                self.simulation = simulation
                self.pending = True

        class Encoder(json.JSONEncoder):
            def default(self, value):
                if isinstance(value, np.ndarray):
                    return value.tolist()
                if isinstance(value, np.generic):
                    return value.item()
                return super().default(value)

        @dataclass
        class PreservedInput:
            variable_name: str
            branch_name: str
            period: Period
            value: object
            storage: str

        person = types.SimpleNamespace(key="person", plural="people", is_person=True)
        household = types.SimpleNamespace(
            key="household", plural="households", is_person=False
        )

        class Holder:
            def __init__(self, population, name):
                self.population = population
                self.simulation = population.simulation
                self.variable = self.simulation.tax_benefit_system.get_variable(name)
                self._memory_storage = Storage()
                self._disk_storage = None
                self._on_disk_storable = False
                self._do_not_store = False

            def _storage_period(self, period):
                return as_period(period)

            def _raise_if_input_contains_nan(self, array):
                assert np.isfinite(array).all()

            def _to_array(self, value, validate_nan=False):
                return np.asarray(value, dtype=float).reshape(1)

            def _record_store(self, *args):
                pass

            def _record_inputs(self, *args):
                pass

            def _evict_fast_cache(self, *args, **kwargs):
                pass

            def _input_unchanged(self, *args):
                return False

            def _stores(self, period, branch_name):
                return self._memory_storage.has(period, branch_name)

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
            cache_blacklist = []
            data_modified = False

            def __init__(self):
                self.variables = {
                    name: types.SimpleNamespace(
                        name=name,
                        entity=person,
                        definition_period="year",
                        is_neutralized=False,
                        value_type=float,
                        set_input=None,
                        end=None,
                    )
                    for name in (
                        *COMPONENTS,
                        *(f"{name}_reported" for name in COMPONENTS),
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

        system = System()

        class Simulation:
            default_role = "member"
            default_input_period = "2024"
            default_calculation_period = "2024"

            def __init__(self, tax_benefit_system=None, populations=None, **kwargs):
                self.tax_benefit_system = tax_benefit_system or system
                self._user_input_keys = set()
                self._user_input_contexts = []
                self._inputs_set = 0
                self._calculations_started = 0
                self.input_variables = []
                self.parent_branch = None
                self.branch_name = "default"
                self.branches = {}
                self._data_storage_dir = None
                self._storage_dir_parent = None
                self.invalidated_caches = set()
                self._fast_cache = {}
                self.start_instant = None
                self.opt_out_cache = False
                self.trace = False
                self.fail_after_store = False
                self.build_from_populations(
                    populations or self.tax_benefit_system.instantiate_entities()
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

            def _drop_values_that_may_depend_on(self, *args):
                pass

            def _get_store_history(self):
                return History()

            def _get_requested_variables(self):
                return set()

            def _drop_computed(self, since=None):
                return sum(
                    holder._drop_computed(since)
                    for population in self.populations.values()
                    for holder in population._holders.values()
                )

            def subsample(self, *args):
                raise NotImplementedError(
                    "Dataset subsampling is outside this storage backend"
                )

            def calculate(self, name, period):
                return self.get_holder(name).get_array(
                    as_period(period), self.branch_name
                )

            def _calculate(self, name, period):
                return self.calculate(name, period)

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
            commons=commons,
            next_sequence_number=next_sequence,
            _calculation_frames=calculation_frames,
            _branch_clone=branch_clone,
            _BranchClone=BranchClone,
            _note_unobserved_activity=lambda: None,
            directory_containing=lambda path: None,
            PreservedUserInput=PreservedInput,
            NpEncoder=Encoder,
            ETERNITY="eternity",
            Dataset=Dataset,
            Simulation=Simulation,
            SimulationBuilder=Builder,
            _get_person_count=lambda values: 1,
            check_type=lambda *args: None,
            PeriodMismatchError=ValueError,
            copy=copy,
        )
        holder_methods = (
            "clone",
            "set_input",
            "_set",
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
        execute(
            core / "holders/helpers.py", ("_is_input", "get_stored_input"), namespace
        )
        sim_methods = (
            "set_input",
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
            next_sequence_number=next_sequence,
            DERIVED_PERIODS_FILE="derived_periods.txt",
            DUMP_FORMAT_FILE="dump_format.txt",
            DUMP_FORMAT_VERSION=1,
            _dump_entity=lambda *args: None,
            _restore_entity=lambda *args: 1,
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
        helpers = module(
            "policyengine_core.holders.helpers",
            _is_input=namespace["_is_input"],
            _period_from_storage_key=as_period,
            get_stored_input=namespace["get_stored_input"],
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
                _note_input_change=lambda *args: None,
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
        hook_namespace = dict(
            json=json,
            ContextVar=ContextVar,
            wraps=wraps,
            Path=Path,
            get_stored_input=namespace["get_stored_input"],
            to_period=as_period,
            NpEncoder=Encoder,
            ETERNITY="eternity",
        )
        execute(
            ROOT / "tools/period_branch.py", ("delete_input_values",), hook_namespace
        )
        # Keep every assignment and function body from the real hook module;
        # execute anew for each example, so ContextVars and stamps stay private.
        exec(compiled_hooks(hook_source), hook_namespace)
        hook_namespace["install_social_security_input_compatibility"]()
        self.Simulation = Simulation
        self.DelegatingSimulation = DelegatingSimulation
        self.Builder = Builder
        self.Dataset = Dataset
        self.system = system
        self.hooks = hook_namespace
        self.dumper = dumper

    def close(self):
        self.stack.close()
