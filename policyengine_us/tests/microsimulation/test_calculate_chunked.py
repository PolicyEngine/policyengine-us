"""Household chunking must preserve real model results and dataset row order.

Python is needed to exercise the dataset/factory API, arbitrary partitions and
simulation lifetime. The 32-household reference is calculated once; only its
arrays survive, so no reference simulation remains live during chunked runs.
"""

import gc
import weakref

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USMultiYearDataset,
    USSingleYearDataset,
)
from policyengine_us.system import system
from policyengine_us.tools.calculate_chunked import calculate_chunked

YEAR = 2026
HOUSEHOLDS = 32
VARIABLES = (
    "tob_revenue_oasdi",
    "tob_revenue_medicare_hi",
    "tob_revenue_total",
    "household_net_income",
    "income_tax",
    "spm_unit_net_income",
    # Exercise outputs for all six entity tables, including person ordering.
    "employment_income",
    "family_weight",
    "marital_unit_weight",
)


def build_chunking_dataset() -> USSingleYearDataset:
    """Several states, multi-unit households and taxable Social Security.

    Entity IDs are sparse, and every entity table has a different unsorted row
    order and nontrivial index. Membership must come from the person links,
    rather than coincident entity positions, ID sorting, or pandas indices.
    """
    records = {entity: [] for entity in US_ENTITIES}
    state_fips = (6, 36, 48, 20, 12)
    for household in range(HOUSEHOLDS):
        household_id = 90_001 + 37 * household
        # Non-binary fractions expose accidental float32 weighted reductions.
        weight = 1.13 + household * 0.137
        records["household"].append(
            {
                "household_id": household_id,
                "household_weight": weight,
                "state_fips": state_fips[household % len(state_fips)],
            }
        )
        # Two tax units in every household; two SPM/family units in half.
        tax_ids = [201_003 + 41 * household + offset for offset in (0, 11)]
        spm_ids = [301_009 + 43 * household + offset for offset in (0, 13)]
        family_ids = [401_011 + 47 * household + offset for offset in (0, 17)]
        marital_ids = [501_019 + 53 * household + offset for offset in (0, 19, 23)]
        for tax_id in tax_ids:
            records["tax_unit"].append(
                {"tax_unit_id": tax_id, "tax_unit_weight": weight}
            )
        for spm_id in spm_ids[: 2 if household % 2 == 0 else 1]:
            records["spm_unit"].append(
                {"spm_unit_id": spm_id, "spm_unit_weight": weight}
            )
        for family_id in family_ids[: 2 if household % 2 == 0 else 1]:
            records["family"].append({"family_id": family_id, "family_weight": weight})
        for marital_id in marital_ids:
            records["marital_unit"].append(
                {"marital_unit_id": marital_id, "marital_unit_weight": weight}
            )
        for member, age in enumerate((72, 68, 42, 12)):
            second_unit = member >= 2
            links = {
                "household": household_id,
                "tax_unit": tax_ids[int(second_unit)],
                "spm_unit": spm_ids[int(second_unit and household % 2 == 0)],
                "family": family_ids[int(second_unit and household % 2 == 0)],
                "marital_unit": marital_ids[max(member - 1, 0)],
            }
            person = {
                "person_id": 601_031 + 59 * household + member * 7,
                "person_weight": weight,
                "age": age,
                "employment_income": (
                    35_000 + household * 1_200 if member == 2 else 0.0
                ),
                "taxable_interest_income": (
                    22_000 + household * 1_500 if member == 0 else 0.0
                ),
                "social_security_retirement": (
                    25_000 + household * 150 if member < 2 else 0.0
                ),
            }
            for entity, entity_id in links.items():
                person[f"person_{entity}_id"] = entity_id
                person[f"person_{entity}_role"] = "member"
            records["person"].append(person)

    tables = {}
    for seed, (entity, rows) in enumerate(records.items()):
        table = pd.DataFrame(rows).sample(frac=1, random_state=100 + seed)
        table.index = 1_001 + np.arange(len(table)) * 3
        tables[entity] = table
    return USSingleYearDataset(**tables, time_period=YEAR)


def make_simulation(dataset):
    # Bypass automatic multi-year projection for this fixed-year fixture.
    if isinstance(dataset, USSingleYearDataset):
        dataset = USMultiYearDataset(datasets=[dataset])
    return Microsimulation(dataset=dataset)


@pytest.fixture(scope="module")
def chunking_dataset():
    return build_chunking_dataset()


@pytest.fixture(scope="module")
def reference(chunking_dataset):
    simulation = make_simulation(chunking_dataset)
    values = {}
    weighted_sums = {}
    weights = {}
    for variable in VARIABLES:
        entity = system.variables[variable].entity.key
        calculated = simulation.calculate(variable, YEAR)
        values[variable] = np.asarray(calculated).copy()
        if entity not in weights:
            weights[entity] = np.asarray(calculated.weights).copy()
        weighted_sums[variable] = float(calculated.sum())
    del calculated
    # Core stores this backreference even for the global default system.
    if getattr(simulation.tax_benefit_system, "simulation", None) is simulation:
        del simulation.tax_benefit_system.simulation
    del simulation
    gc.collect()
    for variable in (
        "tob_revenue_oasdi",
        "tob_revenue_medicare_hi",
        "tob_revenue_total",
    ):
        assert np.any(values[variable] != 0), f"Fixture must exercise {variable}"
    return values, weighted_sums, weights


def assert_matches_reference(result, dataset, reference):
    values, weighted_sums, weights = reference
    expected_entities = {system.variables[var].entity.key for var in VARIABLES}
    assert set(result.entities) == expected_entities
    assert set(result.weighted_sums) == set(VARIABLES)
    for entity, frame in result.entities.items():
        expected_ids = getattr(dataset, entity)[f"{entity}_id"].to_numpy()
        np.testing.assert_array_equal(frame[f"{entity}_id"], expected_ids)
        np.testing.assert_array_equal(frame["weight"], weights[entity])
        assert len(frame) == len(expected_ids)
        assert not frame[f"{entity}_id"].duplicated().any()
    for variable in VARIABLES:
        entity = system.variables[variable].entity.key
        np.testing.assert_array_equal(
            result.entities[entity][variable], values[variable]
        )
        assert result.weighted_sums[variable] == weighted_sums[variable]


@pytest.mark.parametrize("n_chunks", [1, 2, 3, 7])
def test_chunked_real_model_is_elementwise_exact(n_chunks, chunking_dataset, reference):
    # Weak references detect retained simulations and cycles before the next
    # chunk, including branch-to-parent references created by TOB calculations.
    simulations = []
    seen = {entity: [] for entity in US_ENTITIES}

    def factory(dataset):
        assert all(simulation() is None for simulation in simulations)
        single_year = (
            dataset[YEAR] if isinstance(dataset, USMultiYearDataset) else dataset
        )
        household_ids = set(single_year.household.household_id)
        people = chunking_dataset.person[
            chunking_dataset.person.person_household_id.isin(household_ids)
        ]
        pd.testing.assert_frame_equal(single_year.person, people)
        for entity in US_ENTITIES:
            table = getattr(single_year, entity)
            seen[entity].extend(table[f"{entity}_id"])
            if entity not in ("person", "household"):
                expected = getattr(chunking_dataset, entity)
                expected = expected[
                    expected[f"{entity}_id"].isin(people[f"person_{entity}_id"])
                ]
                pd.testing.assert_frame_equal(table, expected)
        simulation = make_simulation(dataset)
        simulations.append(weakref.ref(simulation))
        return simulation

    result = calculate_chunked(
        factory, VARIABLES, YEAR, n_chunks, dataset=chunking_dataset
    )
    assert_matches_reference(result, chunking_dataset, reference)
    assert len(simulations) == n_chunks
    assert all(simulation() is None for simulation in simulations)
    for entity, ids in seen.items():
        expected_ids = getattr(chunking_dataset, entity)[f"{entity}_id"]
        assert len(ids) == len(expected_ids)
        assert set(ids) == set(expected_ids)


@st.composite
def household_partitions(draw):
    n_chunks = draw(st.integers(min_value=1, max_value=7))
    # Every partition is nonempty, while all remaining household assignments
    # vary independently. Chunk labels are intentionally not contiguous rows.
    tail = draw(
        st.lists(
            st.integers(min_value=0, max_value=n_chunks - 1),
            min_size=HOUSEHOLDS - n_chunks,
            max_size=HOUSEHOLDS - n_chunks,
        )
    )
    labels = np.asarray(list(range(n_chunks)) + tail)
    offset = draw(st.integers(min_value=0, max_value=HOUSEHOLDS - 1))
    return n_chunks, np.roll(labels, offset)


@settings(max_examples=4, deadline=None)
@given(partition=household_partitions())
def test_random_household_partitions_are_exact(partition, chunking_dataset, reference):
    n_chunks, household_chunks = partition
    result = calculate_chunked(
        make_simulation,
        VARIABLES,
        YEAR,
        n_chunks,
        dataset=chunking_dataset,
        household_chunks=household_chunks,
    )
    assert_matches_reference(result, chunking_dataset, reference)


def test_multi_year_dataset_preserves_every_year_and_original_input(
    chunking_dataset,
):
    previous = chunking_dataset.copy()
    previous.time_period = str(YEAR - 1)
    previous.person["employment_income"] = previous.person.employment_income * 0.9
    multi = USMultiYearDataset(datasets=[previous, chunking_dataset])
    original = multi.copy()
    seen = []

    def factory(dataset):
        assert isinstance(dataset, USMultiYearDataset)
        assert dataset.years == [YEAR - 1, YEAR]
        household_ids = set(dataset[YEAR].household.household_id)
        for year in dataset.years:
            single = dataset[year]
            for entity in US_ENTITIES:
                table = getattr(original[year], entity)
                if entity == "household":
                    mask = table.household_id.isin(household_ids)
                elif entity == "person":
                    mask = table.person_household_id.isin(household_ids)
                else:
                    people = original[year].person
                    member_ids = people.loc[
                        people.person_household_id.isin(household_ids),
                        f"person_{entity}_id",
                    ]
                    mask = table[f"{entity}_id"].isin(member_ids)
                pd.testing.assert_frame_equal(getattr(single, entity), table[mask])
        seen.append(household_ids)
        return make_simulation(dataset)

    result = calculate_chunked(factory, ["employment_income"], YEAR, 3, dataset=multi)
    np.testing.assert_array_equal(
        result.entities["person"].employment_income,
        chunking_dataset.person.employment_income,
    )
    assert len(seen) == 3
    assert set.union(*seen) == set(chunking_dataset.household.household_id)
    for year in multi.years:
        for entity in US_ENTITIES:
            pd.testing.assert_frame_equal(
                getattr(multi[year], entity), getattr(original[year], entity)
            )


def _snapshot_calculations(simulation, variables, period):
    expected = {}
    for variable in variables:
        calculated = simulation.calculate(variable, period)
        expected[variable] = (
            simulation.tax_benefit_system.variables[variable].entity.key,
            np.asarray(calculated).copy(),
            np.asarray(calculated.weights).copy(),
            float(calculated.sum()),
        )
    return expected


def _assert_snapshot_matches(result, dataset, expected):
    assert set(result.weighted_sums) == set(expected)
    for variable, (entity, values, weights, weighted_sum) in expected.items():
        table = result.entities[entity]
        np.testing.assert_array_equal(
            table[f"{entity}_id"], getattr(dataset, entity)[f"{entity}_id"]
        )
        np.testing.assert_array_equal(table[variable], values)
        np.testing.assert_array_equal(table.weight, weights)
        assert result.weighted_sums[variable] == weighted_sum


def _release_reference_simulation(simulation):
    if getattr(simulation.tax_benefit_system, "simulation", None) is simulation:
        simulation.tax_benefit_system.simulation = None


def test_single_year_factory_automatically_projects_future_inputs(chunking_dataset):
    variables = ("employment_income", "household_weight")
    future_year = YEAR + 1
    # Exercise the normal US constructor, including its automatic dataset
    # extension, rather than the fixed-year wrapper used by the other tests.
    simulation = Microsimulation(dataset=chunking_dataset, dataset_end_year=future_year)
    expected = _snapshot_calculations(simulation, variables, future_year)
    assert np.any(
        expected["employment_income"][1]
        != chunking_dataset.person.employment_income.to_numpy()
    )
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()

    result = calculate_chunked(
        lambda dataset: Microsimulation(dataset=dataset, dataset_end_year=future_year),
        variables,
        future_year,
        3,
        dataset=chunking_dataset,
    )
    _assert_snapshot_matches(result, chunking_dataset, expected)


def test_reform_factory_is_exact_and_releases_its_baseline(chunking_dataset):
    from policyengine_core.reforms import Reform

    variables = ("income_tax", "household_net_income")
    # Share a reform specification; each factory call gets a fresh simulation
    # and policy system. Higher standard deductions have a visible tax effect.
    reform = Reform.from_dict(
        {
            "gov.irs.deductions.standard.amount.JOINT": {
                "2026-01-01.2100-12-31": 50_000
            },
            "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 35_000
            },
        },
        country_id="us",
    )

    def build(dataset):
        return Microsimulation(
            dataset=USMultiYearDataset(datasets=[dataset]), reform=reform
        )

    baseline = make_simulation(chunking_dataset)
    baseline_tax = np.asarray(baseline.calculate("income_tax", YEAR)).copy()
    _release_reference_simulation(baseline)
    del baseline
    gc.collect()

    simulation = build(chunking_dataset)
    expected = _snapshot_calculations(simulation, variables, YEAR)
    assert np.any(expected["income_tax"][1] != baseline_tax)
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()
    references = []

    def factory(dataset):
        assert all(reference() is None for reference in references)
        simulation = build(dataset)
        assert simulation.baseline is not None
        references.extend((weakref.ref(simulation), weakref.ref(simulation.baseline)))
        return simulation

    result = calculate_chunked(factory, variables, YEAR, 2, dataset=chunking_dataset)
    _assert_snapshot_matches(result, chunking_dataset, expected)
    assert all(reference() is None for reference in references)


@pytest.mark.parametrize("multi_year", [False, True], ids=["single-year", "multi-year"])
def test_entity_hdfstore_paths_match_full_calculation(
    tmp_path, chunking_dataset, multi_year
):
    variables = ("employment_income", "household_weight")
    if multi_year:
        previous = chunking_dataset.copy()
        previous.time_period = str(YEAR - 1)
        previous.person["employment_income"] = previous.person.employment_income * 0.9
        source = USMultiYearDataset(datasets=[previous, chunking_dataset])
    else:
        source = chunking_dataset
    path = tmp_path / "chunking.h5"
    source.save(str(path))

    # The direct constructor supports a single-year HDFStore path. Pass the
    # explicit multi-year object for its full-population reference; the chunk
    # API itself must detect and load both on-disk layouts.
    simulation = Microsimulation(
        dataset=source if multi_year else str(path), dataset_end_year=YEAR
    )
    expected = _snapshot_calculations(simulation, variables, YEAR)
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()

    result = calculate_chunked(
        lambda dataset: Microsimulation(dataset=dataset, dataset_end_year=YEAR),
        variables,
        YEAR,
        2,
        dataset=path,
    )
    _assert_snapshot_matches(result, chunking_dataset, expected)
    for variable, entity in (
        ("employment_income", "person"),
        ("household_weight", "household"),
    ):
        actual = result.entities[entity][variable].to_numpy()
        source_values = getattr(chunking_dataset, entity)[variable].to_numpy(
            dtype=actual.dtype
        )
        np.testing.assert_array_equal(actual, source_values)
