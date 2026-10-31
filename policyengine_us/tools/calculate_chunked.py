"""Exact household partitions for calculations that are local to households."""

from dataclasses import dataclass
from functools import lru_cache
import gc
from numbers import Integral
from pathlib import Path

import numpy as np
import pandas as pd

from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USMultiYearDataset,
    USSingleYearDataset,
)


# These formulas reduce across the population, rather than within a household.
# Guard at calculation time so parameter-selected and reform dependencies are
# covered too, including calculations made in branches.
_POPULATION_AGGREGATES = frozenset(
    ("medicaid_slcsp_state_average_cost_index", "medicaid_slcsp_state_denominator")
)


class _HouseholdLocalCalculations:
    @staticmethod
    def _check_household_local(variable_name):
        if variable_name in _POPULATION_AGGREGATES:
            raise ValueError(
                f"Cannot calculate {variable_name} in household chunks: "
                "it aggregates across households. Calculate it on the full dataset."
            )

    def calculate(self, variable_name, *args, **kwargs):
        self._check_household_local(variable_name)
        return super().calculate(variable_name, *args, **kwargs)

    def _calculate(self, variable_name, period=None):
        self._check_household_local(variable_name)
        return super()._calculate(variable_name, period)


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
    if isinstance(dataset, (str, Path)):
        from policyengine_us.system import _resolve_dataset_path

        path = _resolve_dataset_path(str(dataset))
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
            "or entity-table HDFStore path/URL."
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
    simulation options. ``dataset`` accepts US entity-table dataset objects or
    HDFStore paths/URLs. All six entity tables and membership links are required.
    All years are retained; IDs and memberships must be constant across years.

    By default households are split into balanced consecutive chunks. Optional
    ``household_chunks`` supplies one integer in ``[0, n_chunks)`` per source
    household, permitting arbitrary partitions. Empty chunks are skipped.

    Returns ``ChunkedCalculation``: ``entities[entity]`` has source-order rows,
    ``<entity>_id``, ``weight`` (the weights used by Microsimulation), and
    one column per requested variable. ``weighted_sums`` reduces those tables
    in source order, avoiding chunk-dependent floating-point summation order.
    Input weights are never rescaled. Only one chunk simulation is live at once.

    This is exact for household-local calculations. Known Medicaid state
    aggregates and external claiming-tax-unit links are rejected. Custom reform
    formulas must also be household-local: population reductions, ranking and
    random draws depending on population order are not supported.
    """
    if isinstance(n_chunks, bool) or not isinstance(n_chunks, Integral) or n_chunks < 1:
        raise ValueError("n_chunks must be a positive integer.")
    variables = [variables] if isinstance(variables, str) else list(variables)
    if not variables or len(set(variables)) != len(variables):
        raise ValueError("variables must be a nonempty sequence of unique names.")
    if "weight" in variables:
        raise ValueError("weight is reserved for the returned simulation weights.")
    dataset = _load_dataset(dataset)
    years = (
        list(dataset.datasets.values())
        if isinstance(dataset, USMultiYearDataset)
        else [dataset]
    )
    source = years[0]
    positions = _household_positions(source)
    if not len(source.household):
        raise ValueError("dataset must contain at least one household.")
    for year in years[1:]:
        _household_positions(year)
        for entity in US_ENTITIES:
            columns = [f"{entity}_id"]
            if entity == "person":
                columns += [
                    f"person_{group}_id" for group in US_ENTITIES if group != "person"
                ]
            if (
                not getattr(source, entity)[columns]
                .reset_index(drop=True)
                .equals(getattr(year, entity)[columns].reset_index(drop=True))
            ):
                raise ValueError(
                    "Entity IDs and memberships must be identical across years."
                )
    if household_chunks is None:
        assignments = np.empty(len(source.household), dtype=int)
        for chunk, indices in enumerate(
            np.array_split(np.arange(len(assignments)), min(n_chunks, len(assignments)))
        ):
            assignments[indices] = chunk
    else:
        assignments = np.asarray(household_chunks)
        if (
            assignments.shape != (len(source.household),)
            or not np.issubdtype(assignments.dtype, np.integer)
            or (assignments < 0).any()
            or (assignments >= n_chunks).any()
        ):
            raise ValueError(
                "household_chunks must assign each household an integer in [0, n_chunks)."
            )

    tables = {}
    variable_entities = {}
    for chunk in np.unique(assignments):
        masks = {
            entity: assignments[owners] == chunk for entity, owners in positions.items()
        }
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
            for year in years
        ]
        chunk_dataset = (
            USMultiYearDataset(datasets=subsets)
            if isinstance(dataset, USMultiYearDataset)
            else subsets[0]
        )
        simulation = None
        try:
            simulation = sim_factory(chunk_dataset)
            _guard(simulation)
            for name in variables:
                entity = simulation.tax_benefit_system.get_variable(
                    name, check_existence=True
                ).entity.key
                if name in variable_entities and variable_entities[name] != entity:
                    raise ValueError(
                        "sim_factory must use the same variable entities in every chunk."
                    )
                variable_entities[name] = entity
                original_ids = getattr(source, entity)[f"{entity}_id"].to_numpy()
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
            del chunk_dataset, subsets
            gc.collect()
    sums = {
        name: float((tables[entity][name] * tables[entity]["weight"]).sum())
        for name, entity in variable_entities.items()
    }
    return ChunkedCalculation(tables, sums)
