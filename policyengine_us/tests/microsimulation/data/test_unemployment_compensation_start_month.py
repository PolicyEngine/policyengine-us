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
- Filtering: a dataset cut to some households keeps each person's start
  month and months of receipt.
- A column stored for some people but not others raises an error that names
  it.
"""

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset

YEAR = 2024
LATER_YEAR = 2026
COLUMN = "unemployment_compensation_start_month"


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


def test_partly_stored_column_raises_naming_it(people):
    stored = _with_stored_column(people)
    stored.loc[stored.index[:2], COLUMN] = 0
    simulation = Microsimulation(dataset=_dataset(stored))
    with pytest.raises(ValueError, match=COLUMN):
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")


def test_out_of_range_start_month_raises_naming_it(people):
    stored = _with_stored_column(people)
    stored.loc[stored.index[0], COLUMN] = 13
    simulation = Microsimulation(dataset=_dataset(stored))
    with pytest.raises(ValueError, match=COLUMN):
        simulation.calculate("is_receiving_unemployment_compensation", f"{YEAR}-01")
