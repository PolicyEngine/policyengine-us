"""Storing the unemployment compensation start month changes no result.

is_receiving_unemployment_compensation used to place each person's months
of unemployment compensation by hashing person_id (the splitmix64 finalizer,
modulo 12) inside the formula. The dataset build now assigns that start month
and stores it as unemployment_compensation_start_month; the model only
compares months (policyengine-core#500).

Invariants checked on one dataset, against a frozen copy of the retired
formula:
- Neutrality: storing the start month the build derives from person_id
  (splitmix64(person_id) mod 12, plus 1) gives exactly the old results, in
  every month of the base year and of a later, extended year.
- Determinism: two simulations of the same dataset agree.
- Every start month (1-12) with every number of months (0-12) gives one
  block of exactly that many calendar months, starting in the start month
  and wrapping into January.
- Filtering: a dataset cut to some households keeps each person's start
  month and months of receipt.
- A column stored for some people but not others (as zeros or as missing
  values), or stored as all zeros, raises an error that names it. Presence follows the simulation's inputs,
  not the values, so this holds for a column set after construction and for
  one set on a branch too. A reform that neutralizes the column when the
  simulation is built leaves it unsupplied; neutralizing it on a live
  simulation raises.
- Subsampling, on the default branch or a branch whose parent has calculated
  receipt, keeps a missing column missing and a stored one stored.
- A simulation built the way policyengine.py's input-table adapter builds one
  (an empty situation, then the dataset's populations and columns) is a
  household situation to pe-us. Without the column it keeps the retired
  formula's household-position months; with a complete column it gives the
  same months as a Microsimulation of the same file.

TRANSITIONAL: a dataset without the column still hashes person_id. When the
hash is deleted, test_dataset_without_the_column_gives_the_same_results
becomes a test that such a dataset raises.
"""

import numpy as np
import pandas as pd
import pytest

from policyengine_core.reforms import Reform
from policyengine_core.simulations.simulation_builder import SimulationBuilder

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset

YEAR = 2024
LATER_YEAR = 2026
COLUMN = "unemployment_compensation_start_month"
GROUPS = ("household", "tax_unit", "spm_unit", "family", "marital_unit")


def retired_start_month_index(key) -> np.ndarray:
    """Frozen copy of the retired formula's hash: splitmix64(key) mod 12."""
    x = np.asarray(key).astype(np.uint64)
    with np.errstate(over="ignore"):
        x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    x = x ^ (x >> np.uint64(31))
    return (x % np.uint64(12)).astype(int)


def stored_start_month(person_id) -> np.ndarray:
    """The column the dataset build writes: the retired start month, 1-12."""
    return retired_start_month_index(person_id) + 1


def retired_receipt(start_index, months, month) -> np.ndarray:
    """The retired rule: receipt when the month falls in the block."""
    return (month - 1 - start_index) % 12 < months


def _people(households: int = 60, seed: int = 20261025) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sizes = rng.integers(1, 5, size=households)
    household_ids = np.repeat(np.arange(1, households + 1), sizes)
    # CPS-style ids (PH_SEQ * 100 + P_SEQ) on scattered PH_SEQ values, plus a
    # few ids near the top of the engine's int32 range, so the hash sees ids
    # like those in the survey and in cloned builds.
    ph_seq = rng.choice(np.arange(1, 90_000), size=households, replace=False)
    ph_seq[:3] = [2**24 + 7, 20_000_011, 21_474_835]
    position = np.concatenate([np.arange(size) for size in sizes])
    person_id = np.repeat(ph_seq, sizes) * 100 + position + 1
    n = person_id.size
    weeks = rng.integers(0, 53, size=n)
    # Some people report weeks unemployed without unemployment compensation,
    # and some report compensation without weeks (all 12 months).
    compensation = np.where(rng.random(n) < 0.75, rng.integers(500, 20_000, n), 0)
    return pd.DataFrame(
        {
            "person_id": person_id.astype(np.int64),
            "person_household_id": household_ids,
            "person_tax_unit_id": household_ids,
            "person_spm_unit_id": household_ids,
            "person_family_id": household_ids,
            "person_marital_unit_id": household_ids,
            "age": np.full(n, 35.0),
            "weeks_unemployed": weeks.astype(float),
            "unemployment_compensation": compensation.astype(float),
        }
    )


def _dataset(person: pd.DataFrame) -> USSingleYearDataset:
    ids = np.unique(person["person_household_id"])
    return USSingleYearDataset(
        person=person.reset_index(drop=True),
        household=pd.DataFrame(
            {
                "household_id": ids,
                "state_fips": np.full(ids.size, 48),
                "household_weight": np.ones(ids.size),
            }
        ),
        tax_unit=pd.DataFrame({"tax_unit_id": ids}),
        spm_unit=pd.DataFrame({"spm_unit_id": ids}),
        family=pd.DataFrame({"family_id": ids}),
        marital_unit=pd.DataFrame({"marital_unit_id": ids}),
        time_period=YEAR,
    )


def _with_stored_column(person: pd.DataFrame) -> pd.DataFrame:
    return person.assign(**{COLUMN: stored_start_month(person["person_id"])})


def _population_built(person: pd.DataFrame):
    """A simulation built as policyengine.py's input-table adapter builds one.

    The adapter subclasses Microsimulation with no default dataset, starts
    from an empty situation, declares the dataset's populations and sets each
    column other than the ids as an input
    (src/policyengine/tax_benefit_models/us/model.py), so person_id keeps its
    default and the simulation is not over a dataset.
    """

    class InputMicrosimulation(Microsimulation):
        default_dataset = None

    simulation = InputMicrosimulation(situation={}, default_input_period=YEAR)
    builder = SimulationBuilder()
    builder.populations = simulation.tax_benefit_system.instantiate_entities()
    builder.declare_person_entity("person", person["person_id"].values)
    for group in GROUPS:
        link = person[f"person_{group}_id"].values
        builder.declare_entity(group, np.unique(link))
        builder.join_with_persons(
            builder.populations[group], link, np.array(["member"] * link.size)
        )
    simulation.build_from_populations(builder.populations)
    for column in person.columns:
        if column != "person_id" and not column.startswith("person_"):
            simulation.set_input(column, YEAR, person[column].values)
    return simulation


def _receipt_by_month(simulation, year) -> np.ndarray:
    return np.stack(
        [
            np.asarray(
                simulation.calculate(
                    "is_receiving_unemployment_compensation",
                    f"{year}-{month:02d}",
                ).values
            )
            for month in range(1, 13)
        ],
        axis=1,
    )


def _january_start_by_month(simulation, year) -> np.ndarray:
    """Receipt when everyone's block starts in January."""
    months = np.asarray(
        simulation.calculate("unemployment_compensation_months", year).values
    )
    start = np.zeros(months.size, dtype=int)
    return np.stack(
        [retired_receipt(start, months, month) for month in range(1, 13)], axis=1
    )


def _retired_by_month(simulation, year) -> np.ndarray:
    person_id = np.asarray(simulation.calculate("person_id", year).values)
    months = np.asarray(
        simulation.calculate("unemployment_compensation_months", year).values
    )
    start = retired_start_month_index(person_id)
    return np.stack(
        [retired_receipt(start, months, month) for month in range(1, 13)], axis=1
    )


@pytest.fixture(scope="module")
def people() -> pd.DataFrame:
    return _people()


@pytest.fixture(scope="module")
def stored_simulation(people):
    return Microsimulation(dataset=_dataset(_with_stored_column(people)))


def test_engine_sees_the_dataset_person_ids(people, stored_simulation):
    # The engine stores int variables as int32, so the build must hash the
    # ids the engine sees. These ids fit, so the two agree.
    np.testing.assert_array_equal(
        stored_simulation.calculate("person_id", YEAR).values,
        people["person_id"].values,
    )


@pytest.mark.parametrize("year", [YEAR, LATER_YEAR])
def test_stored_start_month_reproduces_the_retired_hash(stored_simulation, year):
    stored = _receipt_by_month(stored_simulation, year)
    assert stored.any() and not stored.all(), "the cases must vary"
    np.testing.assert_array_equal(stored, _retired_by_month(stored_simulation, year))


def test_stored_start_month_is_carried_unchanged_across_years(stored_simulation):
    base = stored_simulation.calculate(COLUMN, YEAR).values
    later = stored_simulation.calculate(COLUMN, LATER_YEAR).values
    np.testing.assert_array_equal(base, later)


def test_dataset_without_the_column_gives_the_same_results(people, stored_simulation):
    # TRANSITIONAL: until the default dataset stores the start month, a
    # dataset without it still hashes person_id. Storing it changes nothing.
    unstored = Microsimulation(dataset=_dataset(people))
    for year in (YEAR, LATER_YEAR):
        np.testing.assert_array_equal(
            _receipt_by_month(unstored, year),
            _receipt_by_month(stored_simulation, year),
        )


def test_two_simulations_of_one_dataset_agree(people, stored_simulation):
    again = Microsimulation(dataset=_dataset(_with_stored_column(people)))
    np.testing.assert_array_equal(
        _receipt_by_month(again, YEAR), _receipt_by_month(stored_simulation, YEAR)
    )


def test_filtered_dataset_keeps_each_persons_months(people, stored_simulation):
    stored = _with_stored_column(people)
    kept = stored["person_household_id"] % 3 == 1
    filtered = Microsimulation(dataset=_dataset(stored[kept]))
    full = pd.DataFrame(
        _receipt_by_month(stored_simulation, YEAR),
        index=stored_simulation.calculate("person_id", YEAR).values,
    )
    cut = pd.DataFrame(
        _receipt_by_month(filtered, YEAR),
        index=filtered.calculate("person_id", YEAR).values,
    )
    pd.testing.assert_frame_equal(cut, full.loc[cut.index])


def test_every_start_month_and_length_gives_one_wrapping_block():
    start, months = np.meshgrid(np.arange(1, 13), np.arange(0, 13), indexing="ij")
    start, months = start.ravel(), months.ravel()
    ids = np.arange(1, start.size + 1)
    person = pd.DataFrame(
        {
            "person_id": ids,
            "person_household_id": ids,
            "person_tax_unit_id": ids,
            "person_spm_unit_id": ids,
            "person_family_id": ids,
            "person_marital_unit_id": ids,
            "age": np.full(ids.size, 35.0),
            "unemployment_compensation_months": months,
            COLUMN: start,
        }
    )
    receipt = _receipt_by_month(Microsimulation(dataset=_dataset(person)), YEAR)
    # Built by counting months forward from the start, not by the formula's
    # modular comparison.
    expected = np.zeros((ids.size, 12), dtype=bool)
    for row, (first, length) in enumerate(zip(start, months)):
        for offset in range(length):
            expected[row, (first - 1 + offset) % 12] = True
    np.testing.assert_array_equal(receipt, expected)
    np.testing.assert_array_equal(receipt.sum(axis=1), months)


def test_partly_stored_column_raises_naming_it(people):
    stored = _with_stored_column(people)
    stored.loc[stored.index[:2], COLUMN] = 0
    simulation = Microsimulation(dataset=_dataset(stored))
    with pytest.raises(ValueError, match=COLUMN):
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_stored_column_with_missing_values_raises_naming_it(people):
    # A column missing for some people arrives as floats with NaN. Core's
    # NaN check covers integer inputs (unlike booleans, which it casts), so
    # the column can't load as complete.
    stored = _with_stored_column(people).astype({COLUMN: float})
    stored.loc[stored.index[:2], COLUMN] = np.nan
    with pytest.raises(ValueError, match=COLUMN):
        simulation = Microsimulation(dataset=_dataset(stored))
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_stored_column_of_zeros_raises_naming_it(people):
    # A dataset that stores the column must fill it, so an all-zero column
    # is not taken for an absent one.
    stored = people.assign(**{COLUMN: 0})
    simulation = Microsimulation(dataset=_dataset(stored))
    with pytest.raises(ValueError, match=COLUMN):
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_start_month_set_after_construction_is_used(people):
    # January differs from the retired hash for most people, so ignoring the
    # input would show.
    simulation = Microsimulation(dataset=_dataset(people))
    simulation.set_input(COLUMN, YEAR, np.ones(len(people), dtype=int))
    receipt = _receipt_by_month(simulation, YEAR)
    np.testing.assert_array_equal(receipt, _january_start_by_month(simulation, YEAR))
    assert (receipt != _retired_by_month(simulation, YEAR)).any()
    partial = Microsimulation(dataset=_dataset(people))
    values = stored_start_month(people["person_id"])
    values[:2] = 0
    partial.set_input(COLUMN, YEAR, values)
    with pytest.raises(ValueError, match=COLUMN):
        partial.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_start_month_of_zeros_set_after_construction_raises(people):
    # Core lists input_variables when the simulation is built, so presence
    # comes from the inputs the simulation holds, not from that list.
    simulation = Microsimulation(dataset=_dataset(people))
    simulation.set_input(COLUMN, YEAR, np.zeros(len(people), dtype=int))
    with pytest.raises(ValueError, match=COLUMN):
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_start_month_applies_forward_from_the_year_it_is_set(people):
    # Core carries an input forward to later periods, never backwards: a
    # year before the first input reads the default 0, which raises.
    later_only = Microsimulation(dataset=_dataset(people))
    later_only.set_input(COLUMN, LATER_YEAR, stored_start_month(people["person_id"]))
    with pytest.raises(ValueError, match=COLUMN):
        later_only.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    carried = Microsimulation(dataset=_dataset(people))
    carried.set_input(COLUMN, YEAR, np.ones(len(people), dtype=int))
    receipt = _receipt_by_month(carried, LATER_YEAR)
    np.testing.assert_array_equal(receipt, _january_start_by_month(carried, LATER_YEAR))
    assert (receipt != _retired_by_month(carried, LATER_YEAR)).any()


def test_subsample_keeps_a_missing_start_month_missing(people):
    # Core's subsample reloads every value a simulation holds as an input,
    # calculated ones included. Receipt calculated before it reads the start
    # month's default, which must not come back as a supplied column of
    # zeros: that would raise for the months not yet calculated.
    calculated = Microsimulation(dataset=_dataset(people))
    calculated.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    untouched = Microsimulation(dataset=_dataset(people))
    for simulation in (calculated, untouched):
        simulation.subsample(n=20, seed="start-month", quantize_weights=False)
    np.testing.assert_array_equal(
        _receipt_by_month(calculated, YEAR), _receipt_by_month(untouched, YEAR)
    )
    np.testing.assert_array_equal(
        _receipt_by_month(untouched, YEAR), _retired_by_month(untouched, YEAR)
    )


def test_subsample_keeps_a_stored_start_month(people):
    stored = Microsimulation(dataset=_dataset(people.assign(**{COLUMN: 1})))
    stored.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    stored.subsample(n=20, seed="start-month", quantize_weights=False)
    np.testing.assert_array_equal(
        _receipt_by_month(stored, YEAR), _january_start_by_month(stored, YEAR)
    )


def test_subsampling_a_branch_keeps_an_inherited_missing_start_month_missing(people):
    # The branch inherits the parent's calculated default for the start month.
    # Subsampling must not reload it as the branch's input: every month the
    # branch has not calculated would then raise.
    parent = Microsimulation(dataset=_dataset(people))
    parent.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    parent_receipt = _receipt_by_month(parent, YEAR)
    branch = parent.get_branch("subsampled")
    branch.subsample(n=20, seed="start-month", quantize_weights=False)
    assert not branch.get_holder(COLUMN).get_input_periods(branch.branch_name)
    np.testing.assert_array_equal(
        _receipt_by_month(branch, YEAR), _retired_by_month(branch, YEAR)
    )
    # The parent keeps its population and its results.
    np.testing.assert_array_equal(_receipt_by_month(parent, YEAR), parent_receipt)


def test_subsampling_a_branch_keeps_an_inherited_stored_start_month(people):
    parent = Microsimulation(dataset=_dataset(people.assign(**{COLUMN: 1})))
    parent.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    branch = parent.get_branch("subsampled")
    branch.subsample(n=20, seed="start-month", quantize_weights=False)
    np.testing.assert_array_equal(
        _receipt_by_month(branch, YEAR), _january_start_by_month(branch, YEAR)
    )


def test_subsampling_a_branch_keeps_a_start_month_set_on_it(people):
    # The branch inherits the parent's calculated default and stores its own
    # input over it. (Receipt isn't calculated first: a value calculated
    # before an input is set stays cached.)
    parent = Microsimulation(dataset=_dataset(people))
    parent.calculate(COLUMN, YEAR)
    branch = parent.get_branch("subsampled")
    branch.set_input(COLUMN, YEAR, np.ones(len(people), dtype=int))
    branch.subsample(n=20, seed="start-month", quantize_weights=False)
    np.testing.assert_array_equal(
        _receipt_by_month(branch, YEAR), _january_start_by_month(branch, YEAR)
    )


def test_start_month_set_on_a_branch_is_supplied_there_only(people, stored_simulation):
    parent = Microsimulation(dataset=_dataset(people))
    branch = parent.get_branch("start_month_of_zeros")
    branch.set_input(COLUMN, YEAR, np.zeros(len(people), dtype=int))
    with pytest.raises(ValueError, match=COLUMN):
        branch.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    # The parent cannot read the branch's input, so it still has no column.
    np.testing.assert_array_equal(
        _receipt_by_month(parent, YEAR), _receipt_by_month(stored_simulation, YEAR)
    )


def test_branch_reads_its_parents_stored_column(people):
    # A start month that differs from the retired hash shows which one the
    # branch used.
    stored = people.assign(**{COLUMN: 1})
    parent = Microsimulation(dataset=_dataset(stored))
    branch = parent.get_branch("reads_the_parent")
    np.testing.assert_array_equal(
        _receipt_by_month(branch, YEAR), _receipt_by_month(parent, YEAR)
    )
    months = np.asarray(
        parent.calculate("unemployment_compensation_months", YEAR).values
    )
    np.testing.assert_array_equal(_receipt_by_month(branch, YEAR).sum(axis=1), months)
    january = _receipt_by_month(branch, YEAR)[:, 0]
    np.testing.assert_array_equal(january, months > 0)


def test_reform_that_neutralizes_the_column_leaves_it_unsupplied(people):
    # Core ignores a dataset's values for a neutralized variable, so the
    # reform simulation has no start month and, for now, hashes person_id.
    # (Its baseline loses the column too: policyengine-core#632.)
    class neutralize_start_month(Reform):
        def apply(self):
            self.neutralize_variable(COLUMN)

    stored = people.assign(**{COLUMN: 1})
    reformed = Microsimulation(dataset=_dataset(stored), reform=neutralize_start_month)
    np.testing.assert_array_equal(
        _receipt_by_month(reformed, YEAR), _retired_by_month(reformed, YEAR)
    )


def test_population_built_simulation_keys_household_position(people):
    simulation = _population_built(people)
    assert not simulation.is_over_dataset
    # The retired formula ranked the default person_id within the household,
    # which is each member's position there.
    position = people.groupby("person_household_id").cumcount().values
    months = np.asarray(
        simulation.calculate("unemployment_compensation_months", YEAR).values
    )
    expected = np.stack(
        [
            retired_receipt(retired_start_month_index(position), months, month)
            for month in range(1, 13)
        ],
        axis=1,
    )
    np.testing.assert_array_equal(_receipt_by_month(simulation, YEAR), expected)


def test_population_built_simulation_follows_a_stored_column(people, stored_simulation):
    # With the column, the adapter gives the dataset's months, as a
    # Microsimulation of the file does, not the household-position months it
    # gave without it. A release that adds the column changes the adapter's
    # results for that reason, and has to be qualified through the adapter.
    stored = _population_built(_with_stored_column(people))
    unstored = _population_built(people)
    np.testing.assert_array_equal(
        _receipt_by_month(stored, YEAR), _receipt_by_month(stored_simulation, YEAR)
    )
    assert (_receipt_by_month(stored, YEAR) != _receipt_by_month(unstored, YEAR)).any()


def test_out_of_range_start_month_raises_naming_it(people):
    stored = _with_stored_column(people)
    stored.loc[stored.index[0], COLUMN] = 13
    simulation = Microsimulation(dataset=_dataset(stored))
    with pytest.raises(ValueError, match=COLUMN):
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_neutralizing_a_stored_column_on_a_live_simulation_raises(people):
    # Neutralizing a variable after the data has loaded keeps its input, so
    # the column still counts as supplied, but core then returns the
    # variable's default, 0, which the start month's check refuses.
    neutralized = Microsimulation(dataset=_dataset(people.assign(**{COLUMN: 1})))
    neutralized.tax_benefit_system.neutralize_variable(COLUMN)
    assert neutralized.get_holder(COLUMN).get_input_periods(neutralized.branch_name)
    with pytest.raises(ValueError, match=COLUMN):
        neutralized.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
    # The neutralization stays with that simulation's own policy.
    untouched = Microsimulation(dataset=_dataset(people.assign(**{COLUMN: 1})))
    np.testing.assert_array_equal(
        _receipt_by_month(untouched, YEAR), _january_start_by_month(untouched, YEAR)
    )
