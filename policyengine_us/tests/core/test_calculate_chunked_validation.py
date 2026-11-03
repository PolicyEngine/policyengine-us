"""Reject invalid household partitions before constructing a simulation."""

import re
import tempfile
import weakref
from pathlib import Path
from types import SimpleNamespace

import h5py
import numpy as np
import pandas as pd
import pytest

from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USMultiYearDataset,
    USSingleYearDataset,
)
from policyengine_us.system import system
from policyengine_us.tools.calculate_chunked import (
    _POPULATION_AGGREGATES,
    _guard,
    calculate_chunked,
)

YEAR = 2026
MARITAL_UNIT_IDS = [91, 92, 37, 38]


@pytest.fixture(autouse=True)
def private_tempdir(tmp_path, monkeypatch):
    # calculate_chunked's mkdtemp and _chunk_directories then see only this
    # test's chunk folders, not another process's in the shared temp folder.
    directory = tmp_path / "tmp"
    directory.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(directory))


@pytest.fixture
def dataset():
    # Two households of two people. Each person is their own marital unit, so
    # a one-household chunk holds two marital units and passes the SSI-spouse
    # guard; every other entity has one row per household.
    ids = np.asarray([91, 37])
    person = pd.DataFrame({"person_id": [503, 504, 101, 102]})
    for entity in US_ENTITIES:
        if entity not in ("person", "marital_unit"):
            person[f"person_{entity}_id"] = np.repeat(ids, 2)
    person["person_marital_unit_id"] = MARITAL_UNIT_IDS
    tables = {"person": person}
    for entity in US_ENTITIES:
        if entity not in ("person", "marital_unit"):
            tables[entity] = pd.DataFrame({f"{entity}_id": ids})
    tables["marital_unit"] = pd.DataFrame({"marital_unit_id": MARITAL_UNIT_IDS})
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


def test_rejects_reserved_weight_column(dataset):
    with pytest.raises(ValueError, match="weight is reserved"):
        calculate(dataset, variables=["weight"])


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
    dataset.person[f"person_{entity}_id"] = 91
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
    dataset.person["medicaid_claiming_tax_unit_id"] = [37, 37, 91, 91]
    with pytest.raises(ValueError, match="claiming_tax_unit_id crosses households"):
        calculate(dataset)


def test_rejects_changed_multi_year_memberships(dataset):
    other = dataset.copy()
    other.time_period = str(YEAR + 1)
    other.person["person_tax_unit_id"] = [37, 37, 91, 91]
    multi = USMultiYearDataset(datasets=[dataset, other])
    with pytest.raises(ValueError, match="memberships must be identical"):
        calculate(multi)


GUARDED = sorted(_POPULATION_AGGREGATES)


def test_guard_covers_known_population_formulas():
    assert set(GUARDED) == {
        "medicaid_slcsp_state_average_cost_index",
        "medicaid_slcsp_state_denominator",
        "household_income_decile",
        "spm_unit_income_decile",
    }


class AggregateSimulation:
    """Exercise aggregate guards without building a country simulation.

    Like Core's ``Simulation._calculate``, ``_calculate`` checks the period
    just before a formula would run. The real-simulation tests below cover the
    Core hook itself.
    """

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

    def _check_period_consistency(self, period, variable):
        pass

    def calculate(self, variable, period, use_weights=False):
        return self._calculate(variable, period)

    def _calculate(self, variable, period=None):
        self._check_period_consistency(period, system.variables[variable])
        if self.route == "branch":
            return self.branches["existing"].calculate(self.aggregate, period)
        if self.route == "baseline":
            return self.baseline.calculate(self.aggregate, period)
        if variable != self.aggregate:
            return self.calculate(self.aggregate, period)
        pytest.fail("Population aggregate must be rejected before formula execution")


@pytest.mark.parametrize("aggregate", GUARDED)
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


def _reader_reform():
    """Add a yearly reader of each guarded variable and one monthly reader."""
    from policyengine_core.reforms import Reform
    from policyengine_core.variables import Variable

    readers = {}
    for aggregate in GUARDED:
        guarded = system.variables[aggregate]

        def formula(unit, period, parameters, aggregate=aggregate):
            return unit(aggregate, period)

        readers[aggregate] = type(
            f"reads_{aggregate}",
            (Variable,),
            {
                "value_type": float,
                "entity": guarded.entity,
                "definition_period": "year",
                "label": f"Reads {aggregate}",
                "formula": formula,
            },
        )

    def monthly_formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_income_decile", period.this_year)

    monthly = type(
        "reads_spm_unit_income_decile_monthly",
        (Variable,),
        {
            "value_type": float,
            "entity": system.variables["spm_unit_income_decile"].entity,
            "definition_period": "month",
            "label": "Reads spm_unit_income_decile each month",
            "formula": monthly_formula,
        },
    )

    class AddReaders(Reform):
        def apply(self):
            for reader in [*readers.values(), monthly]:
                # The country simulation applies a reform more than once.
                self.update_variable(reader)

    return AddReaders


@pytest.fixture(scope="module")
def guarded_simulations():
    """One reformed simulation over a tiny dataset, guarded as chunks are.

    Nothing here runs a guarded formula, so one simulation serves every route.
    """
    from policyengine_us import Microsimulation

    ids = np.asarray([91, 37])
    person = pd.DataFrame({"person_id": [503, 101], "age": [40, 40]})
    for entity in US_ENTITIES:
        if entity != "person":
            person[f"person_{entity}_id"] = ids
    tables = {"person": person}
    for entity in US_ENTITIES:
        if entity != "person":
            tables[entity] = pd.DataFrame({f"{entity}_id": ids})
    tables["household"]["household_weight"] = [1.5, 2.25]
    tables["household"]["state_fips"] = [6, 48]
    single = USSingleYearDataset(**tables, time_period=YEAR)
    simulation = Microsimulation(
        dataset=USMultiYearDataset(datasets=[single]), reform=_reader_reform()
    )
    stored = Microsimulation(dataset=USMultiYearDataset(datasets=[single]))
    stored.set_input("spm_unit_income_decile", YEAR, np.asarray([3, 8]))
    stored.set_input("medicaid_slcsp_state_denominator", YEAR, np.asarray([2.5, 4.0]))
    _guard(simulation)
    _guard(stored)
    yield simulation, stored
    for current in (simulation, simulation.baseline, stored):
        current.tax_benefit_system.simulation = None


def _rejects(calculation):
    with pytest.raises(ValueError, match="aggregates across households"):
        calculation()


@pytest.mark.parametrize("aggregate", GUARDED)
def test_core_hook_guards_every_route(guarded_simulations, aggregate):
    # These are real Core simulations: a renamed Core hook fails here rather
    # than silently dropping the guard.
    simulation, _ = guarded_simulations
    assert simulation.baseline is not None
    _rejects(lambda: simulation.calculate(aggregate, YEAR))
    _rejects(lambda: simulation.calculate(f"reads_{aggregate}", YEAR))
    # A yearly variable requested for a month reaches the hook for its year.
    _rejects(lambda: simulation.calculate(aggregate, f"{YEAR}-01"))
    branch = simulation.get_branch(f"branch_{aggregate}")
    try:
        _rejects(lambda: branch.calculate(aggregate, YEAR))
        _rejects(lambda: branch.calculate(f"reads_{aggregate}", YEAR))
    finally:
        simulation.branches.pop(f"branch_{aggregate}")
    _rejects(lambda: simulation.baseline.calculate(aggregate, YEAR))


def test_core_hook_guards_readers_across_periods(guarded_simulations):
    simulation, _ = guarded_simulations
    # income_decile reaches household_income_decile through its formula.
    _rejects(lambda: simulation.calculate("income_decile", YEAR))
    _rejects(lambda: simulation.baseline.calculate("income_decile", YEAR))
    # A monthly reader requested for a year is summed over its months.
    _rejects(lambda: simulation.calculate("reads_spm_unit_income_decile_monthly", YEAR))
    _rejects(
        lambda: simulation.calculate(
            "reads_spm_unit_income_decile_monthly", f"{YEAR}-03"
        )
    )


def test_guarded_variable_with_stored_value_returns_it(guarded_simulations):
    # No formula reduces across the chunk when the value is stored.
    _, stored = guarded_simulations
    np.testing.assert_array_equal(
        stored.calculate("spm_unit_income_decile", YEAR, use_weights=False), [3, 8]
    )
    np.testing.assert_array_equal(
        stored.calculate("medicaid_slcsp_state_denominator", YEAR, use_weights=False),
        [2.5, 4.0],
    )
    _rejects(lambda: stored.calculate("household_income_decile", YEAR))


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
    dataset.person["employment_income"] = [10_000.0, 0.0, 25_000.0, 0.0]
    # Core uses projected household weights; native input columns still survive.
    dataset.person["person_weight"] = [999.0, 998.0, 888.0, 887.0]
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
    np.testing.assert_array_equal(
        result.entities["person"].weight, [1.5, 1.5, 2.25, 2.25]
    )
    np.testing.assert_array_equal(
        result.entities["household"].household_weight, [1.5, 2.25]
    )
    assert result.weighted_sums["employment_income"] == 71_250.0
    np.testing.assert_array_equal(
        pd.concat(snapshots).person_weight, dataset.person.person_weight
    )
    np.testing.assert_array_equal(
        dataset.person.person_weight, [999.0, 998.0, 888.0, 887.0]
    )


@pytest.mark.parametrize("route", ["baseline", "branch", "popped_branch"])
def test_releases_simulations_retained_by_system_backreferences(dataset, route):
    # A baseline can use a shared system whose backreference keeps the baseline
    # and its parent alive. A removed branch can likewise remain reachable only
    # through its parent's system.simulation pointer.
    shared_system = SimpleNamespace(get_variable=system.get_variable, simulation=None)
    references = []
    factory_calls = []

    def factory(chunk):
        assert all(reference() is None for reference in references)
        assert shared_system.simulation is None
        root = InputSimulation(chunk)
        root.parent_branch = None
        root.tax_benefit_system = SimpleNamespace(
            get_variable=system.get_variable, simulation=root
        )
        child = InputSimulation(chunk)
        child.parent_branch = root
        child.tax_benefit_system = shared_system
        shared_system.simulation = child
        if route == "baseline":
            root.baseline = child
        elif route == "branch":
            root.branches["retained"] = child
        else:
            # Model get_branch(..., clone_system=False), followed by pop().
            root.tax_benefit_system = shared_system
        references.extend((weakref.ref(root), weakref.ref(child)))
        factory_calls.append(True)
        return root

    result = calculate_chunked(factory, ["household_weight"], YEAR, 2, dataset=dataset)

    assert len(factory_calls) == 2
    assert all(reference() is None for reference in references)
    assert shared_system.simulation is None
    np.testing.assert_array_equal(
        result.entities["household"].household_weight,
        dataset.household.household_weight,
    )


def test_cleanup_preserves_unrelated_shared_system_simulation(dataset):
    external_simulation = SimpleNamespace(parent_branch=None)
    shared_system = SimpleNamespace(
        get_variable=system.get_variable, simulation=external_simulation
    )
    references = []
    factory_calls = []

    def factory(chunk):
        assert all(reference() is None for reference in references)
        assert shared_system.simulation is external_simulation
        simulation = InputSimulation(chunk)
        simulation.parent_branch = None
        simulation.tax_benefit_system = shared_system
        references.append(weakref.ref(simulation))
        factory_calls.append(True)
        return simulation

    calculate_chunked(factory, ["household_weight"], YEAR, 2, dataset=dataset)

    assert len(factory_calls) == 2
    assert all(reference() is None for reference in references)
    assert shared_system.simulation is external_simulation


# Variable-centric files: <variable>/<period> arrays, as Core loads them.

PERIODS = (str(YEAR - 1), str(YEAR))


def write_variable_centric(path, dataset, periods=PERIODS, extra=()):
    with h5py.File(path, "w") as file:
        for entity in US_ENTITIES:
            table = getattr(dataset, entity)
            for column in table.columns:
                values = table[column].to_numpy()
                if values.dtype == object:
                    # Population files store strings as fixed-width bytes.
                    values = values.astype("S")
                for period in periods:
                    file.create_dataset(f"{column}/{period}", data=values)
        for name, period, values in extra:
            file.create_dataset(f"{name}/{period}", data=values)
    return path


class FileSimulation:
    """Read a chunk file the way the guard and result checks need it."""

    def __init__(self, path):
        with h5py.File(path, "r") as file:
            self.contents = {
                name: {
                    period: (array.dtype, array[()])
                    for period, array in file[name].items()
                }
                for name in file
            }
        self.tax_benefit_system = system
        self.branches = {}
        self.baseline = None
        self.populations = {
            entity: SimpleNamespace(ids=self.contents[f"{entity}_id"][str(YEAR)][1])
            for entity in US_ENTITIES
        }

    def calculate(self, variable, period, use_weights=False):
        return self.contents[variable][str(YEAR)][1]

    def get_weights(self, variable, period):
        assert system.variables[variable].entity.key == "household"
        return self.contents["household_weight"][str(YEAR)][1]


@pytest.fixture
def variable_centric(tmp_path, dataset):
    dataset.person["person_household_role"] = ["member"] * 4
    dataset.person["employment_income"] = [10_000.0, 0.0, 25_000.0, 0.0]
    extra = [
        # Core ignores names that match no variable, whatever their length.
        ("not_a_policyengine_variable", PERIODS[1], np.arange(5)),
        # A period stored for one variable only must survive too.
        (
            "employment_income",
            "2024",
            np.asarray([1.0, 2.0, 3.0, 4.0], dtype=np.float32),
        ),
    ]
    return write_variable_centric(tmp_path / "population_2026.h5", dataset, extra=extra)


def _chunk_directories():
    return set(Path(tempfile.gettempdir()).glob("policyengine-us-chunk-*"))


def test_variable_centric_chunks_keep_periods_dtypes_and_name(variable_centric):
    before = _chunk_directories()
    paths = []
    simulations = []

    def factory(path):
        assert isinstance(path, str)
        # Only one chunk file exists at a time.
        assert all(not Path(previous).exists() for previous in paths)
        assert _chunk_directories() - before == {Path(path).parent}
        paths.append(path)
        simulations.append(FileSimulation(path))
        return simulations[-1]

    result = calculate_chunked(
        factory, ["household_weight"], YEAR, 2, dataset=str(variable_centric)
    )

    np.testing.assert_array_equal(
        result.entities["household"].household_weight, [1.5, 2.25]
    )
    assert [Path(path).name for path in paths] == ["population_2026.h5"] * 2
    assert not any(Path(path).exists() for path in paths)
    assert _chunk_directories() == before
    with h5py.File(variable_centric, "r") as source:
        names = set(source) - {"not_a_policyengine_variable"}
        for row, simulation in enumerate(simulations):
            assert set(simulation.contents) == names
            for name in names:
                assert set(simulation.contents[name]) == set(source[name])
                for period, (dtype, values) in simulation.contents[name].items():
                    stored = source[name][period]
                    assert dtype == stored.dtype
                    # People and marital units: two rows per household.
                    entity = (
                        "person"
                        if name.endswith("_role")
                        else system.variables[name].entity.key
                    )
                    per = 2 if entity in ("person", "marital_unit") else 1
                    np.testing.assert_array_equal(
                        values, stored[()][row * per : (row + 1) * per]
                    )
        assert source["person_household_role/2026"].dtype == np.dtype("S6")
    roles = [s.contents["person_household_role"]["2026"][1] for s in simulations]
    np.testing.assert_array_equal(np.concatenate(roles), [b"member"] * 4)


def test_variable_centric_chunk_file_is_deleted_after_factory_error(variable_centric):
    before = _chunk_directories()
    paths = []

    def factory(path):
        paths.append(path)
        raise RuntimeError("factory failed")

    with pytest.raises(RuntimeError, match="factory failed"):
        calculate_chunked(
            factory, ["household_weight"], YEAR, 2, dataset=variable_centric
        )
    assert len(paths) == 1
    assert not Path(paths[0]).exists()
    assert _chunk_directories() == before


def _rewrite(path, name, periods, values):
    with h5py.File(path, "a") as file:
        for period in periods:
            del file[f"{name}/{period}"]
            file.create_dataset(f"{name}/{period}", data=values)


@pytest.mark.parametrize(
    "name, values, match",
    [
        ("employment_income", [1.0, 2.0, 3.0], r"employment_income/2025.*person has 4"),
        ("household_weight", [1.0], r"household_weight/2025.*household has 2"),
        ("person_tax_unit_id", [91] * 4, "tax_unit spans multiple households"),
        ("household_id", [91, 91], "household_id must be unique"),
        ("person_household_id", [91, 91, 999, 999], "existing household"),
    ],
)
def test_variable_centric_rejects_invalid_arrays(variable_centric, name, values, match):
    # Every stored period agrees, so only the tested rule can fail.
    _rewrite(variable_centric, name, PERIODS, np.asarray(values))
    with pytest.raises(ValueError, match=match):
        calculate(str(variable_centric))


@pytest.mark.parametrize("name", ["household_id", "person_spm_unit_id"])
def test_variable_centric_rejects_ids_that_change_across_periods(
    variable_centric, name
):
    count = 2 if name == "household_id" else 4
    _rewrite(variable_centric, name, PERIODS[:1], np.repeat([37, 91], count // 2))
    with pytest.raises(ValueError, match="identical across stored periods"):
        calculate(str(variable_centric))


def test_variable_centric_rejects_missing_membership(variable_centric):
    with h5py.File(variable_centric, "a") as file:
        del file["person_family_id"]
    with pytest.raises(ValueError, match="Missing person_family_id"):
        calculate(str(variable_centric))


def test_variable_centric_rejects_external_claiming_tax_unit(variable_centric):
    with h5py.File(variable_centric, "a") as file:
        file.create_dataset(
            f"medicaid_claiming_tax_unit_id/{PERIODS[0]}", data=[37, 37, 91, 91]
        )
    with pytest.raises(ValueError, match="claiming_tax_unit_id crosses households"):
        calculate(str(variable_centric))


def test_rejects_flat_and_periodless_array_files(tmp_path, dataset):
    flat = tmp_path / "population.csv"
    dataset.person.to_csv(flat, index=False)
    with pytest.raises(ValueError, match="Flat-file datasets are not supported"):
        calculate(str(flat))
    arrays = tmp_path / "arrays.h5"
    with h5py.File(arrays, "w") as file:
        for entity in US_ENTITIES:
            file.create_dataset(
                f"{entity}_id", data=getattr(dataset, entity)[f"{entity}_id"]
            )
    with pytest.raises(ValueError, match="<variable>/<period> layout"):
        calculate(str(arrays))


# Formulas that read a weight, build a MicroSeries, test an entity count or
# draw random numbers can depend on the whole simulation. Each must be a weight
# variable's own definition, listed here with the reason it is safe in chunks,
# or guarded in chunks.
_HOUSEHOLD_LOCAL_WEIGHT_READERS = {}
_CHUNK_SAFE_POPULATION_READERS = {
    # Tests whether the simulation holds one marital unit. calculate_chunked
    # rejects a chunk holding exactly one of several marital units.
    "gov/ssa/ssi/eligibility/resources/deemed/_ssi_spouses.py": "chunk guard",
}
_POPULATION_SIGNAL = re.compile(
    r"MicroSeries|[\"'](?:"
    + "|".join(US_ENTITIES)
    + r")_weight[\"']|\.weights\b|\.count\s*==|np\.random|default_rng"
)


def test_population_formulas_are_guarded_or_listed():
    """Scan variable sources for population signals.

    The scan sees weight reads, MicroSeries, ``.count ==`` tests of entity
    sizes and NumPy random draws. It cannot see other whole-array reductions
    (``np.sum``, ``np.unique``, sorting) or branches on ``.any()``/``.all()``,
    and it does not read ``reforms/``; those still need review by hand.
    """
    root = Path(__file__).resolve().parents[2] / "variables"
    unguarded = []
    for path in sorted(root.rglob("*.py")):
        source = path.read_text()
        if not _POPULATION_SIGNAL.search(source):
            continue
        defined = set(re.findall(r"^class (\w+)\(Variable\)", source, re.M))
        relative = path.relative_to(root).as_posix()
        if (
            defined & {f"{entity}_weight" for entity in US_ENTITIES}
            or defined & _POPULATION_AGGREGATES
            or relative in _HOUSEHOLD_LOCAL_WEIGHT_READERS
            or relative in _CHUNK_SAFE_POPULATION_READERS
        ):
            continue
        unguarded.append(relative)
    assert not unguarded, (
        "Guard these in calculate_chunked._POPULATION_AGGREGATES or list them "
        f"with a reason: {unguarded}"
    )


def _spouse_and_dependent_households():
    """Household 1: a 70-year-old and a 40-year-old dependent in one marital
    and tax unit, the dependent holding $100,000 of countable resources.
    Household 2: one 30-year-old.

    Unchunked, ssi is [0, 0, 0] and spousal resource deeming applies to the
    first person. Household 1 alone holds one marital unit, so _ssi_spouses
    rules the pair out as a couple and the first person's ssi is $11,928.
    """
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "age": [70, 40, 30],
            "is_tax_unit_dependent": [False, True, False],
            "ssi_countable_resources": [0.0, 100_000.0, 0.0],
        }
    )
    tables = {"person": person}
    for entity in US_ENTITIES:
        if entity != "person":
            person[f"person_{entity}_id"] = [1, 1, 2]
            tables[entity] = pd.DataFrame({f"{entity}_id": [1, 2]})
    tables["household"]["household_weight"] = [1.0, 1.0]
    return USSingleYearDataset(**tables, time_period=YEAR)


def test_rejects_chunk_holding_one_of_several_marital_units():
    households = _spouse_and_dependent_households()
    with pytest.raises(ValueError, match="exactly one marital unit"):
        calculate(households, household_chunks=[0, 1])
    # The whole file in one chunk holds both marital units and is accepted.
    result = calculate_chunked(
        InputSimulation,
        ["household_weight"],
        YEAR,
        2,
        dataset=households,
        household_chunks=[0, 0],
    )
    assert result.weighted_sums == {"household_weight": 2.0}


def test_rejects_one_marital_unit_chunk_before_building_any_chunk(dataset):
    # Household 37's two people now share one marital unit. The first default
    # chunk (household 91, two marital units) is valid, so the guard must run
    # for every chunk before the first is built: never_build fails otherwise.
    dataset.person["person_marital_unit_id"] = [91, 92, 37, 37]
    dataset.marital_unit.drop(index=dataset.marital_unit.index[3], inplace=True)
    with pytest.raises(ValueError, match="exactly one marital unit"):
        calculate(dataset)


def test_accepts_file_holding_a_single_marital_unit():
    # The whole file is one marital unit, so the chunk pairs SSI spouses
    # exactly as the unchunked simulation does.
    person = pd.DataFrame({"person_id": [1, 2]})
    tables = {"person": person}
    for entity in US_ENTITIES:
        if entity != "person":
            person[f"person_{entity}_id"] = [1, 1]
            tables[entity] = pd.DataFrame({f"{entity}_id": [1]})
    tables["household"]["household_weight"] = [1.0]
    one = USSingleYearDataset(**tables, time_period=YEAR)
    result = calculate_chunked(
        InputSimulation, ["household_weight"], YEAR, 1, dataset=one
    )
    assert result.weighted_sums == {"household_weight": 1.0}


def test_marital_unit_check_counts_only_chunks_that_hold_households(dataset):
    # Labels need only be integers below n_chunks. Counting units per possible
    # label (np.bincount with minlength=n_chunks) would try to allocate 8 TiB.
    result = calculate_chunked(
        InputSimulation,
        ["household_weight"],
        YEAR,
        2**40 + 1,
        dataset=dataset,
        household_chunks=[2**40, 0],
    )
    np.testing.assert_array_equal(
        result.entities["household"].household_weight, [1.5, 2.25]
    )


def test_non_hdf5_file_with_h5_suffix_gets_flat_file_error(tmp_path, dataset):
    path = tmp_path / "population.h5"
    dataset.person.to_csv(path, index=False)
    with pytest.raises(ValueError, match="Flat-file datasets are not supported"):
        calculate(str(path))


def _reform_adding_an_input():
    from policyengine_core.reforms import Reform
    from policyengine_core.variables import Variable

    from policyengine_us.entities import Person

    class reform_only_input(Variable):
        value_type = float
        entity = Person
        definition_period = "year"
        label = "Input only a reform defines"

    class reform_only_output(Variable):
        value_type = float
        entity = Person
        definition_period = "year"
        label = "Twice the reform-only input"

        def formula(person, period, parameters):
            return 2 * person("reform_only_input", period)

    class AddInput(Reform):
        def apply(self):
            self.update_variable(reform_only_input)
            self.update_variable(reform_only_output)

    return AddInput


def test_rejects_stored_names_only_the_factory_system_defines(tmp_path, dataset):
    from policyengine_us import Microsimulation

    stored = np.asarray([200.0, 400.0, 600.0, 800.0])
    path = write_variable_centric(
        tmp_path / "population.h5",
        dataset,
        extra=[("reform_only_input", str(YEAR), stored)],
    )
    reform = _reform_adding_an_input()
    # Unchunked, Core loads the stored input through the reformed system; a
    # chunk file, built against the country system, would leave it out.
    whole = Microsimulation(dataset=str(path), reform=reform)
    np.testing.assert_array_equal(
        whole.calculate("reform_only_output", YEAR, use_weights=False), 2 * stored
    )
    reformed = whole.tax_benefit_system

    def factory(chunk):
        # Only the chunk system matters; reuse the unchunked reformed one.
        simulation = FileSimulation(chunk)
        simulation.tax_benefit_system = reformed
        return simulation

    before = _chunk_directories()
    with pytest.raises(ValueError, match="reform_only_input are stored in the file"):
        calculate_chunked(
            factory,
            ["household_weight"],
            YEAR,
            2,
            dataset=str(path),
        )
    assert _chunk_directories() == before
