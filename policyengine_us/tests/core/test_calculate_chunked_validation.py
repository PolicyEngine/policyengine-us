"""Reject invalid household partitions before constructing a simulation."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USMultiYearDataset,
    USSingleYearDataset,
)
from policyengine_us.system import system
from policyengine_us.tools.calculate_chunked import calculate_chunked

YEAR = 2026


@pytest.fixture
def dataset():
    ids = np.asarray([91, 37])
    person = pd.DataFrame({"person_id": [503, 101]})
    for entity in US_ENTITIES:
        if entity != "person":
            person[f"person_{entity}_id"] = ids
    tables = {"person": person}
    for entity in US_ENTITIES:
        if entity != "person":
            tables[entity] = pd.DataFrame({f"{entity}_id": ids})
    tables["household"]["household_weight"] = [1.5, 2.25]
    return USSingleYearDataset(**tables, time_period=YEAR)


def never_build(_dataset):
    pytest.fail("Invalid input must be rejected before constructing a simulation")


def calculate(dataset, **kwargs):
    return calculate_chunked(
        never_build,
        kwargs.pop("variables", ["income_tax"]),
        YEAR,
        kwargs.pop("n_chunks", 2),
        dataset=dataset,
        **kwargs,
    )


@pytest.mark.parametrize("n_chunks", [0, -1, True, 1.5])
def test_rejects_invalid_chunk_counts(dataset, n_chunks):
    with pytest.raises(ValueError, match="positive integer"):
        calculate(dataset, n_chunks=n_chunks)


@pytest.mark.parametrize("variables", [[], ["income_tax", "income_tax"]])
def test_rejects_empty_or_duplicate_variables(dataset, variables):
    with pytest.raises(ValueError, match="nonempty.*unique"):
        calculate(dataset, variables=variables)


@pytest.mark.parametrize("assignments", [[0], [[0], [1]], [0.0, 1.0], [-1, 0], [0, 2]])
def test_rejects_invalid_household_assignments(dataset, assignments):
    with pytest.raises(ValueError, match="household_chunks"):
        calculate(dataset, household_chunks=assignments)


@pytest.mark.parametrize("entity", US_ENTITIES)
def test_rejects_duplicate_entity_ids(dataset, entity):
    table = getattr(dataset, entity)
    table.loc[table.index[1], f"{entity}_id"] = table[f"{entity}_id"].iloc[0]
    with pytest.raises(ValueError, match=f"{entity}_id.*unique"):
        calculate(dataset)


@pytest.mark.parametrize("entity", ["tax_unit", "spm_unit", "family", "marital_unit"])
def test_rejects_entity_spanning_households(dataset, entity):
    dataset.person[f"person_{entity}_id"] = [91, 91]
    with pytest.raises(ValueError, match=f"{entity} spans multiple households"):
        calculate(dataset)


@pytest.mark.parametrize(
    "entity", ["household", "tax_unit", "spm_unit", "family", "marital_unit"]
)
def test_rejects_missing_membership_target(dataset, entity):
    dataset.person.loc[0, f"person_{entity}_id"] = 999
    with pytest.raises(ValueError, match="existing household|Unknown.*membership"):
        calculate(dataset)


@pytest.mark.parametrize("entity", ["tax_unit", "spm_unit", "family", "marital_unit"])
def test_rejects_unreferenced_group_entity(dataset, entity):
    table = getattr(dataset, entity)
    table.loc[len(table)] = [999]
    with pytest.raises(
        ValueError, match=f"Every {entity} must have at least one person"
    ):
        calculate(dataset)


def test_rejects_external_claiming_tax_unit(dataset):
    dataset.person["medicaid_claiming_tax_unit_id"] = [37, 91]
    with pytest.raises(ValueError, match="claiming_tax_unit_id crosses households"):
        calculate(dataset)


def test_rejects_changed_multi_year_memberships(dataset):
    other = dataset.copy()
    other.time_period = str(YEAR + 1)
    other.person["person_tax_unit_id"] = [37, 91]
    multi = USMultiYearDataset(datasets=[dataset, other])
    with pytest.raises(ValueError, match="memberships must be identical"):
        calculate(multi)


class AggregateSimulation:
    """Exercise aggregate guards without building a country simulation."""

    def __init__(self, dataset, aggregate, route):
        self.tax_benefit_system = system
        self.populations = {
            entity: SimpleNamespace(
                ids=getattr(dataset, entity)[f"{entity}_id"].to_numpy()
            )
            for entity in US_ENTITIES
        }
        self.aggregate = aggregate
        self.route = route
        self.branches = {}
        self.baseline = None
        if route in ("branch", "baseline"):
            target = AggregateSimulation(dataset, aggregate, "direct")
            if route == "branch":
                self.branches["existing"] = target
            else:
                self.baseline = target

    def calculate(self, variable, period, use_weights=False):
        return self._calculate(variable, period)

    def _calculate(self, variable, period=None):
        if self.route == "branch":
            return self.branches["existing"].calculate(self.aggregate, period)
        if self.route == "baseline":
            return self.baseline.calculate(self.aggregate, period)
        if variable != self.aggregate:
            return self.calculate(self.aggregate, period)
        pytest.fail("Population aggregate must be rejected before formula execution")


@pytest.mark.parametrize(
    "aggregate",
    ["medicaid_slcsp_state_average_cost_index", "medicaid_slcsp_state_denominator"],
)
@pytest.mark.parametrize("route", ["direct", "dependency", "branch", "baseline"])
def test_rejects_population_aggregates_in_dependency_graph(dataset, aggregate, route):
    variable = aggregate if route == "direct" else "income_tax"
    with pytest.raises(ValueError, match="aggregates across households"):
        calculate_chunked(
            lambda chunk: AggregateSimulation(chunk, aggregate, route),
            [variable],
            YEAR,
            2,
            dataset=dataset,
        )


class InputSimulation:
    def __init__(self, dataset):
        self.dataset = dataset
        self.tax_benefit_system = system
        self.branches = {}
        self.baseline = None
        self.populations = {
            entity: SimpleNamespace(
                ids=getattr(dataset, entity)[f"{entity}_id"].to_numpy()
            )
            for entity in US_ENTITIES
        }

    def calculate(self, variable, period, use_weights=False):
        return self._calculate(variable, period)

    def _calculate(self, variable, period=None):
        entity = system.variables[variable].entity.key
        return getattr(self.dataset, entity)[variable].to_numpy()

    def get_weights(self, variable, period):
        entity = system.variables[variable].entity.key
        household = self.dataset.household.set_index("household_id")
        if entity == "household":
            return self.dataset.household.household_weight.to_numpy()
        assert entity == "person"
        return household.loc[
            self.dataset.person.person_household_id, "household_weight"
        ].to_numpy()


def test_skips_empty_chunks_and_preserves_native_and_projected_weights(dataset):
    dataset.person["employment_income"] = [10_000.0, 25_000.0]
    # Core uses projected household weights; native input columns still survive.
    dataset.person["person_weight"] = [999.0, 888.0]
    snapshots = []

    def factory(chunk):
        snapshots.append(chunk.person.copy())
        return InputSimulation(chunk)

    result = calculate_chunked(
        factory,
        ["employment_income", "household_weight"],
        YEAR,
        5,
        dataset=dataset,
    )
    assert len(snapshots) == 2
    np.testing.assert_array_equal(
        result.entities["person"].person_id, dataset.person.person_id
    )
    np.testing.assert_array_equal(result.entities["person"].weight, [1.5, 2.25])
    np.testing.assert_array_equal(
        result.entities["household"].household_weight, [1.5, 2.25]
    )
    assert result.weighted_sums["employment_income"] == 71_250.0
    np.testing.assert_array_equal(
        pd.concat(snapshots).person_weight, dataset.person.person_weight
    )
    np.testing.assert_array_equal(dataset.person.person_weight, [999.0, 888.0])
