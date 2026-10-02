"""County must stay the household's county in branches reused across years.

``tax_unit_itemizes`` branches the simulation into ``itemizing`` and
``not_itemizing`` (each with a nested ``no_salt``), and later years reuse
those branches. A branch stores what it calculates under its own name, so
the county formula's stored-county read has to use the branch name: it used
to read the default branch's value for the latest known period, found
nothing for a year only the branch had calculated, and returned ``None``.
Core then fell back to its own carry-over. Carrying over only inputs
(PolicyEngine/policyengine-core#562) left those branches at
``County.UNKNOWN``, which raised ``ParameterNotFoundError`` for Maryland
child care rates in a 2025-2027 run over the enhanced CPS; carrying over the
latest calculated value (core master) left a branch at ``UNKNOWN`` whenever
it had calculated a later year first.

These pass on both core versions.
"""

from itertools import permutations

import numpy as np
import pandas as pd
import pytest

from policyengine_core.periods import period as as_period
from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)

DATASET_YEAR = 2024
COUNTY_FIPS = ["24031", "36047", "06037"]
# None of these is its state's first county, so a fall back to
# first_county_in_state shows up as a wrong county.
EXPECTED = [
    "MONTGOMERY_COUNTY_MD",
    "KINGS_COUNTY_NY",
    "LOS_ANGELES_COUNTY_CA",
]
YEARS = (2025, 2026, 2027)


def _dataset(county_fips: list) -> USSingleYearDataset:
    n = len(county_fips)
    ids = np.arange(1, n + 1)
    person = pd.DataFrame(
        {
            "person_id": ids,
            "person_household_id": ids,
            "person_tax_unit_id": ids,
            "person_spm_unit_id": ids,
            "person_family_id": ids,
            "person_marital_unit_id": ids,
            "age": np.full(n, 40.0),
            "employment_income": np.full(n, 100_000.0),
        }
    )
    household = pd.DataFrame(
        {
            "household_id": ids,
            "state_fips": np.array([int(fips[:2]) for fips in COUNTY_FIPS]),
            "county_fips": county_fips,
            "household_weight": np.full(n, 1.0),
        }
    )
    return USSingleYearDataset(
        person=person,
        household=household,
        tax_unit=pd.DataFrame({"tax_unit_id": ids}),
        spm_unit=pd.DataFrame({"spm_unit_id": ids}),
        family=pd.DataFrame({"family_id": ids}),
        marital_unit=pd.DataFrame({"marital_unit_id": ids}),
        time_period=DATASET_YEAR,
    )


def _simulation(stored: str) -> Microsimulation:
    """A dataset storing either ``county_fips`` or one year's ``county``.

    The loader extends a dataset's columns to later years, so a ``county``
    column would be stored for every year and never reach the formula.
    Storing the county for the dataset's year only, with no county FIPS,
    makes later years carry it forward (falling back would give each state's
    first county instead).
    """
    if stored == "county_fips":
        return Microsimulation(dataset=_dataset(COUNTY_FIPS))
    simulation = Microsimulation(dataset=_dataset([""] * len(COUNTY_FIPS)))
    simulation.set_input("county", DATASET_YEAR, County.encode(np.array(EXPECTED)))
    return simulation


def _counties(simulation, year) -> list:
    return simulation.calculate("county_str", year).tolist()


@pytest.mark.parametrize("stored", ["county_fips", "county"])
@pytest.mark.parametrize("years", list(permutations(YEARS)), ids=str)
def test_branch_reused_across_years_keeps_the_county(stored, years):
    simulation = _simulation(stored)
    itemizing = simulation.get_branch("itemizing")
    no_salt = itemizing.get_branch("no_salt")

    for year in years:
        for label, branch in (("itemizing", itemizing), ("no_salt", no_salt)):
            assert _counties(branch, year) == EXPECTED, (label, year)
    for year in years:
        assert _counties(simulation, year) == EXPECTED, ("default", year)


@pytest.mark.parametrize("stored", ["county_fips", "county"])
def test_branch_created_in_one_year_keeps_the_county_in_later_years(stored):
    """The enhanced CPS order: each year the simulation, then its branches.

    The ``itemizing`` branch is created after the simulation has calculated
    the first year's county, calculates the second year itself, and then
    holds no default-branch value for it when the third year asks.
    """
    simulation = _simulation(stored)
    branches = {}
    for year in YEARS:
        assert _counties(simulation, year) == EXPECTED, ("default", year)
        if not branches:
            branches["itemizing"] = simulation.get_branch("itemizing")
            branches["no_salt"] = branches["itemizing"].get_branch("no_salt")
        for label, branch in branches.items():
            assert _counties(branch, year) == EXPECTED, (label, year)


@pytest.mark.parametrize("stored", ["county_fips", "county"])
@pytest.mark.parametrize(
    "requests",
    [
        # Every order of these three year-and-simulation requests, with the
        # branches created before any of them.
        list(order)
        for order in permutations(
            [("default", 2025), ("itemizing", 2026), ("no_salt", 2027)]
        )
    ]
    + [
        list(order)
        for order in permutations(
            [("itemizing", 2027), ("default", 2026), ("no_salt", 2025)]
        )
    ],
    ids=str,
)
def test_county_does_not_depend_on_the_order_of_requests(stored, requests):
    simulation = _simulation(stored)
    itemizing = simulation.get_branch("itemizing")
    simulations = {
        "default": simulation,
        "itemizing": itemizing,
        "no_salt": itemizing.get_branch("no_salt"),
    }
    for label, year in requests:
        assert _counties(simulations[label], year) == EXPECTED, (label, year)
    # Every simulation then reads the same county for every year.
    for label, each in simulations.items():
        for year in YEARS:
            assert _counties(each, year) == EXPECTED, (label, year)


def test_a_period_only_another_branch_can_read_is_skipped():
    """With nothing readable, county comes from ``county_fips``."""
    simulation = _simulation("county_fips")
    holder = simulation.get_holder("county")
    holder.put_in_cache(
        County.encode(np.array(["ALBANY_COUNTY_NY"] * len(COUNTY_FIPS))),
        as_period(2030),
        "sibling",
    )

    assert _counties(simulation, 2026) == EXPECTED


def test_the_latest_period_the_branch_can_read_wins():
    simulation = _simulation("county")
    branch = simulation.get_branch("moved")
    moved = ["BALTIMORE_COUNTY_MD", "QUEENS_COUNTY_NY", "SAN_DIEGO_COUNTY_CA"]
    branch.set_input("county", 2026, County.encode(np.array(moved)))

    # The branch reads its own 2026 county; the simulation it was branched
    # from cannot, and keeps the dataset's.
    assert _counties(branch, 2027) == moved
    assert _counties(simulation, 2027) == EXPECTED
