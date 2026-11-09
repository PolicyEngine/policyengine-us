"""Exact household partitions for calculations that are local to households."""

from dataclasses import dataclass
from functools import lru_cache
import gc
from numbers import Integral
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

import numpy as np
import pandas as pd

from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USMultiYearDataset,
    USSingleYearDataset,
)


# These formulas reduce or rank across every unit in the simulation, rather
# than within a household: the Medicaid state aggregates sum by state, and the
# income deciles rank with MicroSeries.decile_rank. Guard at calculation time
# so parameter-selected and reform dependencies are covered too, including
# calculations made in branches, and readers such as income_decile.
_POPULATION_AGGREGATES = frozenset(
    (
        "medicaid_slcsp_state_average_cost_index",
        "medicaid_slcsp_state_denominator",
        "household_income_decile",
        "spm_unit_income_decile",
    )
)


class _HouseholdLocalCalculations:
    """Reject population aggregates just before their formula would run.

    Core's ``Simulation._calculate`` calls ``_check_period_consistency`` after
    the stored-value lookups and before the formula, once per formula
    evaluation, and the check returns before any dependency starts. Hooking it
    adds no frames to the dependency chain, unlike overriding ``calculate``.
    A stored value is returned without the check: no formula reduces then.
    """

    def _check_period_consistency(self, period, variable):
        if variable.name in _POPULATION_AGGREGATES:
            raise ValueError(
                f"Cannot calculate {variable.name} in household chunks: "
                "it aggregates across households. Calculate it on the full dataset."
            )
        return super()._check_period_consistency(period, variable)


@lru_cache(maxsize=None)
def _guarded_class(simulation_class):
    # Core clones preserve the simulation class, so new branches inherit the
    # guard without changing global classes or other callers' simulations.
    return type(
        f"HouseholdLocal{simulation_class.__name__}",
        (_HouseholdLocalCalculations, simulation_class),
        {},
    )


def _guard(simulation, seen=None):
    seen = set() if seen is None else seen
    if id(simulation) in seen:
        return
    seen.add(id(simulation))
    if hasattr(simulation, "drop_computed_arrays"):
        # A factory may warm caches. Recompute dependencies under the guard so
        # a cached dependent cannot conceal a population-wide aggregation.
        simulation.drop_computed_arrays()
        # Chunk datasets share descriptive names; they must not read or write
        # full-population macro-cache files under those names.
        simulation.macro_cache_read = False
        simulation.macro_cache_write = False
    if not isinstance(simulation, _HouseholdLocalCalculations):
        simulation.__class__ = _guarded_class(type(simulation))
    for branch in simulation.branches.values():
        _guard(branch, seen)
    baseline = getattr(simulation, "baseline", None)
    if baseline is not None:
        _guard(baseline, seen)


def _detach_simulation_links(root):
    """Release systems' references to this chunk and its owned branches.

    A reform baseline can use the globally shared baseline system. Its
    ``simulation`` reference otherwise retains the baseline and its parent
    after the factory's result has been deleted.
    """
    pending = [root]
    seen = set()
    while pending:
        simulation = pending.pop()
        if id(simulation) in seen:
            continue
        seen.add(id(simulation))
        system = simulation.tax_benefit_system
        owner = getattr(system, "simulation", None)
        ancestors = set()
        while owner is not None and id(owner) not in ancestors:
            if owner is root:
                system.simulation = None
                break
            ancestors.add(id(owner))
            owner = getattr(owner, "parent_branch", None)
        pending.extend(getattr(simulation, "branches", {}).values())
        baseline = getattr(simulation, "baseline", None)
        if baseline is not None:
            pending.append(baseline)


@dataclass
class ChunkedCalculation:
    """Entity tables in source order, and sums using simulation weights."""

    entities: dict[str, pd.DataFrame]
    weighted_sums: dict[str, float]


def _load_dataset(dataset):
    """Return an entity-table dataset, or a variable-centric file source."""
    if isinstance(dataset, (str, Path)):
        from policyengine_us.system import (
            _is_hdfstore_format,
            _resolve_dataset_path,
        )

        path = _resolve_dataset_path(str(dataset))
        try:
            entity_tables = _is_hdfstore_format(path)
        except Exception:
            # PyTables raises its own error for a file that is not HDF5.
            entity_tables = False
        if not entity_tables:
            return _VariableCentricFile(path)
        with pd.HDFStore(path, mode="r") as store:
            multi_year = any(key.startswith("/person/") for key in store.keys())
        dataset = (
            USMultiYearDataset(file_path=path)
            if multi_year
            else USSingleYearDataset(file_path=path)
        )
    if not isinstance(dataset, (USSingleYearDataset, USMultiYearDataset)):
        raise TypeError(
            "dataset must be a USSingleYearDataset, USMultiYearDataset, "
            "or an entity-table HDFStore or variable-centric h5 path/URL."
        )
    return dataset


def _household_positions(dataset):
    """Validate the partition and map every entity row to a household row."""
    person = dataset.person
    household_ids = pd.Index(dataset.household.household_id)
    if not household_ids.is_unique or household_ids.hasnans:
        raise ValueError("household_id must be unique and nonmissing.")
    people_households = household_ids.get_indexer(person.person_household_id)
    if (people_households < 0).any():
        raise ValueError("Every person must belong to an existing household.")
    positions = {"household": np.arange(len(household_ids))}
    for entity in US_ENTITIES:
        table = getattr(dataset, entity)
        id_column = f"{entity}_id"
        if id_column not in table:
            raise ValueError(
                f"Missing {id_column}; all six entity tables are required."
            )
        ids = pd.Index(table[id_column])
        if not ids.is_unique or ids.hasnans:
            raise ValueError(f"{id_column} must be unique and nonmissing.")
        if entity == "person":
            positions[entity] = people_households
        elif entity != "household":
            links = person[f"person_{entity}_id"]
            if (ids.get_indexer(links) < 0).any():
                raise ValueError(f"Unknown person_{entity}_id membership.")
            membership = (
                pd.DataFrame({"id": links.to_numpy(), "household": people_households})
                .groupby("id", sort=False)
                .household
            )
            if (membership.nunique() != 1).any():
                raise ValueError(f"A {entity} spans multiple households.")
            owners = membership.first().reindex(ids)
            if owners.isna().any():
                raise ValueError(f"Every {entity} must have at least one person.")
            positions[entity] = owners.to_numpy(dtype=int)
    if len(np.unique(people_households)) != len(household_ids):
        raise ValueError("Every household must have at least one person.")

    # Medicaid can refer to a claiming tax unit explicitly. Its population-wide
    # lookup is local only when a known claimant lives in the same household.
    if "medicaid_claiming_tax_unit_id" in person:
        tax_ids = pd.Index(dataset.tax_unit.tax_unit_id)
        claimant = tax_ids.get_indexer(person.medicaid_claiming_tax_unit_id)
        known = (claimant >= 0) & (person.medicaid_claiming_tax_unit_id.to_numpy() > 0)
        if (positions["tax_unit"][claimant[known]] != people_households[known]).any():
            raise ValueError("medicaid_claiming_tax_unit_id crosses households.")
    return positions


class _EntityTables:
    """Entity-table datasets: chunks are dataset objects of the same type."""

    # Chunks copy every column, so no stored name is left out.
    unmatched = ()

    def __init__(self, dataset):
        self.dataset = dataset
        self.years = (
            list(dataset.datasets.values())
            if isinstance(dataset, USMultiYearDataset)
            else [dataset]
        )
        source = self.years[0]
        self.positions = _household_positions(source)
        self.household_count = len(source.household)
        if not self.household_count:
            raise ValueError("dataset must contain at least one household.")
        for year in self.years[1:]:
            _household_positions(year)
            for entity in US_ENTITIES:
                columns = [f"{entity}_id"]
                if entity == "person":
                    columns += [
                        f"person_{group}_id"
                        for group in US_ENTITIES
                        if group != "person"
                    ]
                if (
                    not getattr(source, entity)[columns]
                    .reset_index(drop=True)
                    .equals(getattr(year, entity)[columns].reset_index(drop=True))
                ):
                    raise ValueError(
                        "Entity IDs and memberships must be identical across years."
                    )

    def ids(self, entity):
        return getattr(self.years[0], entity)[f"{entity}_id"].to_numpy()

    def chunk(self, masks):
        subsets = [
            USSingleYearDataset(
                **{
                    entity: getattr(year, entity)
                    .iloc[np.flatnonzero(masks[entity])]
                    .copy()
                    for entity in US_ENTITIES
                },
                time_period=int(year.time_period),
            )
            for year in self.years
        ]
        return (
            USMultiYearDataset(datasets=subsets)
            if isinstance(self.dataset, USMultiYearDataset)
            else subsets[0]
        )

    def release(self, chunk):
        pass


_GROUPS = tuple(entity for entity in US_ENTITIES if entity != "person")
# Core reads these from the first stored period as the population structure.
_STRUCTURE = tuple(f"{entity}_id" for entity in US_ENTITIES) + tuple(
    f"person_{group}_id" for group in _GROUPS
)
# Core's loader also reads membership roles, which are not variables.
_ROLES = frozenset(f"person_{group}_role" for group in _GROUPS) | {"role"}


class _VariableCentricFile:
    """An h5py file of ``<variable>/<period>`` arrays, as Core loads it.

    Arrays stay on disk. Each chunk is written to a temporary file in the same
    layout, under the source file's name, and is deleted after its simulation.
    """

    def __init__(self, path):
        import h5py

        from policyengine_us.system import system

        self.path = Path(path)
        if self.path.suffix != ".h5":
            # Core loads a file without the .h5 suffix as a CSV flat file.
            raise ValueError(
                f"{self.path} is not an entity-table HDFStore or a "
                "variable-centric .h5 file. Flat-file datasets are not "
                "supported; convert them to one of those layouts."
            )
        self.arrays = {}
        # Stored names that match no country-system variable, left out of
        # chunk files; calculate_chunked checks them against the factory's.
        self.unmatched = []
        try:
            file = h5py.File(self.path, "r")
        except OSError as error:
            # h5py raises OSError for a file with an .h5 suffix that is not HDF5.
            raise ValueError(
                f"{self.path} is not an entity-table HDFStore or a "
                "variable-centric .h5 file. Flat-file datasets are not "
                "supported; convert them to one of those layouts."
            ) from error
        with file:
            names = list(file.keys())
            if not names or isinstance(file[names[0]], h5py.Dataset):
                raise ValueError(
                    f"{self.path} does not use the variable-centric "
                    "<variable>/<period> layout; only that layout and entity "
                    "tables are supported."
                )
            for name in names:
                if name in _ROLES:
                    entity = "person"
                elif name in system.variables:
                    entity = system.variables[name].entity.key
                else:
                    # Core's loader ignores names that match no variable in
                    # the simulation's system; a reform can add one.
                    self.unmatched.append(name)
                    continue
                if not isinstance(file[name], h5py.Group):
                    raise ValueError(f"{name} must be a group of one array per period.")
                self.arrays[name] = (entity, list(file[name].keys()))
            # A group with no periods holds no array for Core to read.
            missing = [
                name
                for name in _STRUCTURE
                if name not in self.arrays or not self.arrays[name][1]
            ]
            if missing:
                raise ValueError(
                    f"Missing {', '.join(missing)}; every entity ID and person "
                    "membership array is required."
                )
            self.counts = {
                entity: file[f"{entity}_id"][self.arrays[f"{entity}_id"][1][0]].shape[0]
                for entity in US_ENTITIES
            }
            for name, (entity, stored_periods) in self.arrays.items():
                for period in stored_periods:
                    shape = file[name][period].shape
                    if shape != (self.counts[entity],):
                        raise ValueError(
                            f"{name}/{period} has shape {shape}, but {entity} "
                            f"has {self.counts[entity]} rows."
                        )
            structure = {}
            for name in _STRUCTURE:
                stored_periods = self.arrays[name][1]
                first = file[name][stored_periods[0]][()]
                for period in stored_periods[1:]:
                    if not np.array_equal(file[name][period][()], first):
                        raise ValueError(
                            "Entity IDs and memberships must be identical "
                            "across stored periods."
                        )
                structure[name] = first
            claimants = [None]
            if "medicaid_claiming_tax_unit_id" in self.arrays:
                group = file["medicaid_claiming_tax_unit_id"]
                claimants = [
                    group[period][()]
                    for period in self.arrays["medicaid_claiming_tax_unit_id"][1]
                ]
        self.structure = structure
        for claimant in claimants:
            self.positions = _household_positions(self._tables(claimant))
        self.household_count = self.counts["household"]
        if not self.household_count:
            raise ValueError("dataset must contain at least one household.")

    def _tables(self, claimant):
        tables = {
            entity: pd.DataFrame({f"{entity}_id": self.structure[f"{entity}_id"]})
            for entity in _GROUPS
        }
        person = {"person_id": self.structure["person_id"]}
        for group in _GROUPS:
            person[f"person_{group}_id"] = self.structure[f"person_{group}_id"]
        if claimant is not None:
            person["medicaid_claiming_tax_unit_id"] = claimant
        tables["person"] = pd.DataFrame(person)
        return SimpleNamespace(**tables)

    def ids(self, entity):
        return self.structure[f"{entity}_id"]

    def chunk(self, masks):
        import h5py

        directory = Path(tempfile.mkdtemp(prefix="policyengine-us-chunk-"))
        try:
            path = directory / self.path.name
            with h5py.File(self.path, "r") as source, h5py.File(path, "w") as chunk:
                for name, (entity, stored_periods) in self.arrays.items():
                    group = chunk.create_group(name)
                    for period in stored_periods:
                        array = source[name][period]
                        group.create_dataset(
                            period, data=array[()][masks[entity]], dtype=array.dtype
                        )
        except BaseException:
            shutil.rmtree(directory, ignore_errors=True)
            raise
        return str(path)

    def release(self, chunk):
        shutil.rmtree(Path(chunk).parent, ignore_errors=True)


def calculate_chunked(
    sim_factory,
    variables,
    period,
    n_chunks,
    *,
    dataset,
    household_chunks=None,
):
    """Calculate numeric variables on disjoint, whole-household partitions.

    ``sim_factory(dataset)`` must return a fresh PolicyEngine-US Microsimulation
    and preserve its dataset's population/order. It controls reforms and other
    simulation options. ``dataset`` accepts US entity-table dataset objects,
    entity-table HDFStore paths/URLs, and variable-centric h5 paths/URLs: files
    of ``<variable>/<period>`` arrays, as population projection files store
    them. All six entity ID arrays and membership links are required. All years
    are retained; IDs and memberships must be constant across years.

    For entity tables the factory receives a dataset object of the source's
    type. For a variable-centric file it receives ``str`` path to a temporary
    file in the same layout, holding every stored period with its dtype under
    the source file's name, for ``Microsimulation(dataset=path)``. Names that
    match no country-system variable are left out, as Core's loader ignores
    them; the helper raises if the factory's system (a reform, say) defines
    one. Only one
    chunk file exists at once; it is deleted after its chunk, on failure too.
    Flat files are not supported.

    By default households are split into balanced consecutive chunks. Optional
    ``household_chunks`` supplies one integer in ``[0, n_chunks)`` per source
    household, permitting arbitrary partitions. Empty chunks are skipped.

    Returns ``ChunkedCalculation``: ``entities[entity]`` has source-order rows,
    ``<entity>_id``, ``weight`` (the weights used by Microsimulation), and
    one column per requested variable. ``weighted_sums`` reduces those tables
    in source order, avoiding chunk-dependent floating-point summation order.
    Input weights are never rescaled. Only one chunk simulation is live at once.

    This is exact for household-local calculations. Known Medicaid state
    aggregates and the household and SPM unit income deciles are rejected
    when their formulas would run; a rejected variable with a stored value
    returns that value, since no formula runs. External claiming-tax-unit
    links, and a chunk holding exactly one of several marital units (which
    can pair SSI spouses differently), are rejected before any chunk is built.
    Custom reform formulas must also be household-local: population
    reductions, ranking and random draws depending on population order are
    not supported.
    """
    if isinstance(n_chunks, bool) or not isinstance(n_chunks, Integral) or n_chunks < 1:
        raise ValueError("n_chunks must be a positive integer.")
    variables = [variables] if isinstance(variables, str) else list(variables)
    if not variables or len(set(variables)) != len(variables):
        raise ValueError("variables must be a nonempty sequence of unique names.")
    if "weight" in variables:
        raise ValueError("weight is reserved for the returned simulation weights.")
    dataset = _load_dataset(dataset)
    source = (
        dataset if isinstance(dataset, _VariableCentricFile) else _EntityTables(dataset)
    )
    positions = source.positions
    if household_chunks is None:
        assignments = np.empty(source.household_count, dtype=int)
        for chunk, indices in enumerate(
            np.array_split(np.arange(len(assignments)), min(n_chunks, len(assignments)))
        ):
            assignments[indices] = chunk
    else:
        assignments = np.asarray(household_chunks)
        if (
            assignments.shape != (source.household_count,)
            or not np.issubdtype(assignments.dtype, np.integer)
            or (assignments < 0).any()
            or (assignments >= n_chunks).any()
        ):
            raise ValueError(
                "household_chunks must assign each household an integer in [0, n_chunks)."
            )

    # _ssi_spouses.py tests whether the simulation holds one marital unit.
    # Count each nonempty chunk's units before any chunk is built; empty
    # chunks are skipped, and labels can be any integers below n_chunks.
    _, marital_units = np.unique(
        assignments[positions["marital_unit"]], return_counts=True
    )
    if len(positions["marital_unit"]) > 1 and (marital_units == 1).any():
        raise ValueError(
            "A chunk holding exactly one marital unit can pair SSI spouses "
            "differently from the whole file (_ssi_spouses.py); use fewer "
            "chunks or different household_chunks."
        )
    tables = {}
    variable_entities = {}
    for chunk in np.unique(assignments):
        masks = {
            entity: assignments[owners] == chunk for entity, owners in positions.items()
        }
        chunk_dataset = None
        simulation = None
        try:
            chunk_dataset = source.chunk(masks)
            simulation = sim_factory(chunk_dataset)
            _guard(simulation)
            dropped = (
                sorted(
                    set(source.unmatched) & set(simulation.tax_benefit_system.variables)
                )
                if source.unmatched
                else []
            )
            if dropped:
                raise ValueError(
                    f"{', '.join(dropped)} are stored in the file and defined by "
                    "the factory's system but not the country system, so chunk "
                    "files cannot carry them. Store them in an entity-table "
                    "dataset or add the variables to the country system."
                )
            for name in variables:
                entity = simulation.tax_benefit_system.get_variable(
                    name, check_existence=True
                ).entity.key
                if name in variable_entities and variable_entities[name] != entity:
                    raise ValueError(
                        "sim_factory must use the same variable entities in every chunk."
                    )
                variable_entities[name] = entity
                original_ids = source.ids(entity)
                if not np.array_equal(
                    simulation.populations[entity].ids, original_ids[masks[entity]]
                ):
                    raise ValueError(
                        "sim_factory must preserve dataset entity IDs and row order."
                    )
                values = np.asarray(
                    simulation.calculate(name, period, use_weights=False)
                ).copy()
                if not np.issubdtype(values.dtype, np.number) and values.dtype != bool:
                    raise TypeError(
                        f"{name} is not numeric; weighted sums require numeric variables."
                    )
                weights = simulation.get_weights(name, period)
                if weights is None:
                    raise ValueError(
                        f"No simulation weights are available for {name} in {period}."
                    )
                # MicroSeries converts calculation weights to float64 before
                # multiplying; match that even for float32 dataset weights.
                weights = np.asarray(weights, dtype=float).copy()
                count = int(masks[entity].sum())
                if values.shape != (count,) or weights.shape != (count,):
                    raise ValueError(
                        "Calculations and weights must have one value per entity."
                    )
                if entity not in tables:
                    tables[entity] = pd.DataFrame(
                        {
                            f"{entity}_id": original_ids.copy(),
                            "weight": np.empty(len(original_ids), dtype=weights.dtype),
                        }
                    )
                table = tables[entity]
                if name not in table:
                    table[name] = np.empty(len(table), dtype=values.dtype)
                table.loc[masks[entity], name] = values
                table.loc[masks[entity], "weight"] = weights
        finally:
            # Populations, branches and systems can refer back to a simulation.
            # Collection here is deliberate: the next factory must not overlap.
            if simulation is not None:
                _detach_simulation_links(simulation)
            del simulation
            gc.collect()
            if chunk_dataset is not None:
                # After collection, so no simulation still reads a chunk file.
                source.release(chunk_dataset)
            del chunk_dataset
    sums = {
        name: float((tables[entity][name] * tables[entity]["weight"]).sum())
        for name, entity in variable_entities.items()
    }
    return ChunkedCalculation(tables, sums)
