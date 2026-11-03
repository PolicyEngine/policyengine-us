"""Household chunking must preserve real model results and dataset row order.

Python is needed to exercise the dataset/factory API, arbitrary partitions and
simulation lifetime. The 32-household reference is calculated once; only its
arrays survive, so no reference simulation remains live during chunked runs.

Partition cases use the country's parameter-lending clone route: branches keep
the complete, unchanged parameter tree and history, with copy-on-write for
reforms, while entities, variable metadata and provider receipts remain private.
Rebuilding the same history for every equivalent partition would dominate this
API test's runtime. The separate TOB sequencing test lends the tree only to its
reference, main's algorithm; the helper's branches there use ordinary clones.
The retained default policy graph is frozen before any simulation is built,
avoiding repeated GC scans of it. New simulation/branch cycles remain in normal
GC generations and must still pass the weak-reference collection checks.
"""

import gc
import sys
import tempfile
import weakref
from contextlib import contextmanager
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import pytest
from hypothesis import example, given, settings, strategies as st

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USMultiYearDataset,
    USSingleYearDataset,
)
from policyengine_us.system import system
from policyengine_us.tools.calculate_chunked import _guard, calculate_chunked

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


@contextmanager
def frozen_heap():
    """Leave what is alive now out of later collections.

    Collections inside the block then scan only objects created inside it,
    which include every simulation and branch the weak-reference checks follow.
    """
    owns_freeze = gc.get_freeze_count() == 0
    if owns_freeze:
        gc.collect()
        gc.freeze()
    try:
        yield
    finally:
        if owns_freeze:
            gc.unfreeze()


@contextmanager
def lent_parameter_history():
    """Give cloned systems the unchanged parameter tree instead of a copy."""
    import policyengine_us.spm as spm

    original = spm.clone_spm_system

    def clone(source, *, copy_receipts=True, parameters=None):
        tree = source.parameters if parameters is None else parameters
        # Lending creates another reader even when the source just acquired a
        # private reform tree. Keep the country's write barrier armed for both
        # readers; a parameter reform still pays for its own detached clone.
        spm.mark_tree_shared(tree)
        return original(source, copy_receipts=copy_receipts, parameters=tree)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(spm, "clone_spm_system", clone)
        yield


@pytest.fixture(scope="module", autouse=True)
def lend_unchanged_parameter_history():
    # Scope the optimization to this module. In particular, importing fixture
    # builders from test_tob_sequencing does not apply it to that test module.
    with frozen_heap(), lent_parameter_history():
        yield


@pytest.fixture(autouse=True)
def private_tempdir(tmp_path, monkeypatch):
    # calculate_chunked's mkdtemp and _chunk_directories then see only this
    # test's chunk folders, not another process's in the shared temp folder.
    directory = tmp_path / "tmp"
    directory.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(directory))


def build_chunking_dataset() -> USSingleYearDataset:
    """Several states, multi-unit households and taxable Social Security.

    Entity IDs are sparse, and every entity table has a different unsorted row
    order and nontrivial index. Membership must come from the person links,
    rather than coincident entity positions, ID sorting, or pandas indices.
    """
    records = {entity: [] for entity in US_ENTITIES}
    state_fips = (6, 48, 12, 53, 32)
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
            # As in the signed TOB fixtures, these units report no itemized
            # medical or SALT deductions. Keep optional sales-tax tables and
            # premium attribution out of repeated income-tax counterfactuals;
            # the standard-deduction choice and all requested formulas remain
            # endogenous.
            records["tax_unit"].append(
                {
                    "tax_unit_id": tax_id,
                    "tax_unit_weight": weight,
                    "itemized_medical_expenses": 0.0,
                    "salt_deduction": 0.0,
                }
            )
        for unit_offset, spm_id in enumerate(spm_ids[: 2 if household % 2 == 0 else 1]):
            # These positive-income units do not take up TANF. Supplying the
            # take-up input avoids unrelated monthly eligibility calculations
            # in each tax branch and in the net-income resource chain.
            records["spm_unit"].append(
                {
                    "spm_unit_id": spm_id,
                    "spm_unit_weight": weight,
                    "takes_up_tanf_if_eligible": False,
                    # Observed annual benefits and expenses keep this dataset
                    # test independent of unrelated eligibility networks.
                    "snap": 1_200.0 if household == 0 and unit_offset == 1 else 0.0,
                    "housing_assistance": 0.0,
                    "spm_unit_medical_out_of_pocket_expenses": (
                        600.0 + 20 * household + unit_offset
                    ),
                    # Nobody reports childcare expenses or subsidy receipt.
                    "nv_child_care_subsidies": 0.0,
                    "ca_child_care_subsidies": 0.0,
                    "wa_child_care_subsidies": 0.0,
                }
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
                # Nobody reports SSI or WIC receipt. Core distributes these
                # annual flow inputs across their twelve monthly periods.
                "ssi": 0.0,
                "wic": 0.0,
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
    _release_reference_simulation(simulation)
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


def calculate_with_checked_chunks(chunking_dataset, n_chunks, household_chunks=None):
    """Calculate VARIABLES with a factory that checks every chunk it receives.

    Each chunk's person and group tables must equal its households' source
    rows, in source order. Weak references detect retained simulations and
    cycles before the next chunk, including branch-to-parent references
    created by TOB calculations. Returns the result and the chunks built.
    """
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
        factory,
        VARIABLES,
        YEAR,
        n_chunks,
        dataset=chunking_dataset,
        household_chunks=household_chunks,
    )
    assert all(simulation() is None for simulation in simulations)
    for entity, ids in seen.items():
        expected_ids = getattr(chunking_dataset, entity)[f"{entity}_id"]
        assert len(ids) == len(expected_ids)
        assert set(ids) == set(expected_ids)
    return result, len(simulations)


# Three chunks catch order errors that two cannot; the smallest of the three
# default chunks still holds 10 households. The partition property below runs
# the same chunk checks on smaller, uneven and interleaved chunks.
@pytest.mark.parametrize("n_chunks", [1, 2, 3])
def test_chunked_real_model_is_elementwise_exact(n_chunks, chunking_dataset, reference):
    result, built = calculate_with_checked_chunks(chunking_dataset, n_chunks)
    assert_matches_reference(result, chunking_dataset, reference)
    assert built == n_chunks


MAX_PARTITION_CHUNKS = 7
# Seven chunks of 1 to 11 households. 7 is coprime with 32, so multiplying row
# numbers by it permutes the households and interleaves the chunks.
UNEVEN_LABELS = np.repeat(np.arange(MAX_PARTITION_CHUNKS), [1, 2, 3, 4, 5, 6, 11])[
    np.arange(HOUSEHOLDS) * 7 % HOUSEHOLDS
]


@st.composite
def household_partitions(draw):
    n_chunks = draw(st.integers(min_value=1, max_value=MAX_PARTITION_CHUNKS))
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


# Hypothesis generates the simplest partition, one chunk labelled 0, first. In
# CI its ci profile derandomizes, so the second generated example is one fixed
# pseudo-random partition; elsewhere it is random. The strategy uses every
# label it draws, so it never leaves a chunk empty. The explicit examples pin
# both ends of its range: every household in one chunk, labelled 3 so that the
# other six labels are empty and skipped; and seven uneven, interleaved chunks.
@example(partition=(MAX_PARTITION_CHUNKS, np.full(HOUSEHOLDS, 3)))
@example(partition=(MAX_PARTITION_CHUNKS, UNEVEN_LABELS))
@settings(max_examples=2, deadline=None)
@given(partition=household_partitions())
def test_random_household_partitions_are_exact(partition, chunking_dataset, reference):
    n_chunks, household_chunks = partition
    result, built = calculate_with_checked_chunks(
        chunking_dataset, n_chunks, household_chunks
    )
    assert_matches_reference(result, chunking_dataset, reference)
    assert built == len(np.unique(household_chunks))


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
    """Detach reference simulations without using production cleanup code."""
    owned = []
    seen = set()
    pending = [simulation]
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        owned.append(current)
        pending.extend(current.branches.values())
        baseline = getattr(current, "baseline", None)
        if baseline is not None:
            pending.append(baseline)
    for current in owned:
        policy = current.tax_benefit_system
        if id(getattr(policy, "simulation", None)) in seen:
            policy.simulation = None


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


def test_reform_factory_is_exact_and_releases_its_baseline(chunking_dataset, reference):
    from policyengine_core.reforms import Reform
    from policyengine_us.spm import clone_spm_system

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
        # The country clone preserves instance-level variable metadata and
        # provider state while avoiding repeated country/parameter loading.
        return Microsimulation(
            dataset=USMultiYearDataset(datasets=[dataset]),
            tax_benefit_system=clone_spm_system(system),
            reform=reform,
        )

    # The module reference calculated unreformed income_tax on this dataset
    # with make_simulation, as a separate baseline simulation would.
    baseline_tax = reference[0]["income_tax"]

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
    constructor_options = {} if multi_year else {"dataset_end_year": YEAR}
    simulation = Microsimulation(
        dataset=source if multi_year else str(path), **constructor_options
    )
    expected = _snapshot_calculations(simulation, variables, YEAR)
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()

    result = calculate_chunked(
        lambda dataset: Microsimulation(dataset=dataset, **constructor_options),
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


# Population projection files store <variable>/<period> arrays, which Core's
# variable-centric loader reads. The same 32 households are written that way.
TOB_VARIABLES = ("tob_revenue_oasdi", "tob_revenue_medicare_hi", "tob_revenue_total")


def write_variable_centric(dataset, path):
    with h5py.File(path, "w") as file:
        for entity in US_ENTITIES:
            table = getattr(dataset, entity)
            for column in table.columns:
                values = table[column].to_numpy()
                if values.dtype == object:
                    # Roles are stored as fixed-width byte strings.
                    values = values.astype("S")
                file.create_dataset(f"{column}/{YEAR}", data=values)
        # Core's loader ignores a name that matches no variable, whatever its
        # length, so the chunked route must too.
        file.create_dataset(f"not_a_policyengine_variable/{YEAR}", data=np.arange(5))
    return str(path)


@pytest.fixture(scope="module")
def variable_centric_path(chunking_dataset, tmp_path_factory):
    return write_variable_centric(
        chunking_dataset, tmp_path_factory.mktemp("population") / "population.h5"
    )


def _parameter_reform():
    from policyengine_core.reforms import Reform

    return Reform.from_dict(
        {
            # A lower base threshold widens benefit inclusion.
            "gov.irs.social_security.taxability.threshold.base.main.JOINT": {
                "2026-01-01.2100-12-31": 20_000
            },
        },
        country_id="us",
    )


@pytest.fixture(scope="module")
def variable_centric_reference(variable_centric_path, reference):
    simulation = Microsimulation(dataset=variable_centric_path)
    expected = _snapshot_calculations(simulation, TOB_VARIABLES, YEAR)
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()
    # Both loaders read the same households to the same results.
    values, weighted_sums, weights = reference
    for variable, (entity, actual, actual_weights, total) in expected.items():
        np.testing.assert_array_equal(actual, values[variable])
        np.testing.assert_array_equal(actual_weights, weights[entity])
        assert total == weighted_sums[variable]
    return expected


def _chunk_directories():
    return set(Path(tempfile.gettempdir()).glob("policyengine-us-chunk-*"))


@pytest.mark.parametrize("n_chunks", [1, 2, 3])
def test_variable_centric_file_is_elementwise_exact(
    n_chunks, chunking_dataset, variable_centric_path, variable_centric_reference
):
    before = _chunk_directories()
    paths = []
    with h5py.File(variable_centric_path, "r") as file:
        source_roles = file[f"person_household_role/{YEAR}"][()]

    def factory(path):
        assert isinstance(path, str) and Path(path).name == "population.h5"
        assert all(not Path(previous).exists() for previous in paths)
        assert _chunk_directories() - before == {Path(path).parent}
        with h5py.File(path, "r") as chunk:
            assert "not_a_policyengine_variable" not in chunk
            roles = chunk[f"person_household_role/{YEAR}"]
            assert roles.dtype == source_roles.dtype == np.dtype("S6")
            people = len(chunk[f"person_id/{YEAR}"])
            np.testing.assert_array_equal(roles[()], source_roles[:people])
        paths.append(path)
        return Microsimulation(dataset=path)

    result = calculate_chunked(
        factory, TOB_VARIABLES, YEAR, n_chunks, dataset=variable_centric_path
    )
    _assert_snapshot_matches(result, chunking_dataset, variable_centric_reference)
    assert len(paths) == n_chunks
    assert not any(Path(path).exists() for path in paths)
    assert _chunk_directories() == before


def test_variable_centric_file_is_exact_under_reform(
    chunking_dataset, variable_centric_path, variable_centric_reference
):
    simulation = Microsimulation(
        dataset=variable_centric_path, reform=_parameter_reform()
    )
    expected = _snapshot_calculations(simulation, TOB_VARIABLES, YEAR)
    assert any(
        np.any(expected[name][1] != variable_centric_reference[name][1])
        for name in TOB_VARIABLES
    ), "The reform must change TOB on the fixture"
    # The chunks share this run's reformed system instead of each loading the
    # country system again with the reform. The reform-factory test above
    # still builds a reformed simulation, with its baseline, for every chunk.
    policy = simulation.tax_benefit_system
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()
    result = calculate_chunked(
        lambda path: Microsimulation(dataset=path, tax_benefit_system=policy),
        TOB_VARIABLES,
        YEAR,
        2,
        dataset=variable_centric_path,
    )
    # Collect the reformed parameter tree here, not in the next test.
    del policy
    gc.collect()
    _assert_snapshot_matches(result, chunking_dataset, expected)


def _deepest_stack(calculation):
    depth = 0
    deepest = 0

    def profile(frame, event, arg):
        nonlocal depth, deepest
        if event == "call":
            depth += 1
            deepest = max(deepest, depth)
        elif event == "return":
            depth -= 1

    sys.setprofile(profile)
    try:
        calculation()
    finally:
        sys.setprofile(None)
    return deepest


def test_guard_adds_no_frames_per_dependency(chunking_dataset):
    # One household, as in one chunk. A guard on calculate or _calculate adds
    # frames to every variable in the chain; the period-check hook adds them
    # only while it runs, before any dependency starts.
    households = chunking_dataset.household.household_id.iloc[:1]
    people = chunking_dataset.person.person_household_id.isin(households)
    tables = {"person": chunking_dataset.person[people], "household": None}
    tables["household"] = chunking_dataset.household[
        chunking_dataset.household.household_id.isin(households)
    ]
    for entity in US_ENTITIES:
        if entity not in tables:
            table = getattr(chunking_dataset, entity)
            members = tables["person"][f"person_{entity}_id"]
            tables[entity] = table[table[f"{entity}_id"].isin(members)]
    one_household = USSingleYearDataset(**tables, time_period=YEAR)
    depths = {}
    for guarded in (False, True):
        simulation = make_simulation(one_household)
        if guarded:
            _guard(simulation)
        else:
            simulation.drop_computed_arrays()
            simulation.macro_cache_read = simulation.macro_cache_write = False
        depths[guarded] = _deepest_stack(
            lambda: simulation.calculate("income_tax", YEAR)
        )
        _release_reference_simulation(simulation)
        del simulation
        gc.collect()
    # The chain is long: each variable costs several frames.
    assert depths[False] > 300
    assert 0 <= depths[True] - depths[False] <= 3, depths
