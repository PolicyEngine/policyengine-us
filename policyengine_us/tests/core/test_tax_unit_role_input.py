"""Tax-unit roles supplied by a population dataset.

The Populace US build's tax-unit constructor (microunit, called from
microcosm-frame) assigns every person a role - HEAD, SPOUSE or DEPENDENT - and
writes it to the person column ``tax_unit_role_input``. The role variables use
it when supplied and fall back to age ordering when not.

The build also writes its constructor's filing status to a tax-unit column,
``filing_status_input``. Filing status is a policy calculation, so the model
does not read that column: ``filing_status`` is computed from the unit's
members, including the supplied roles, and the filing rules.

The YAML tests cover household situations. These cover what the YAML runner
cannot: the error contract, the column contract with the producer, and the
dataset loading path, where the columns arrive as strings and must hold in
every year the loader extends the data to.
"""

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.system import system

YEAR = 2024


def _situation(people: dict) -> dict:
    return {
        "people": {
            name: {
                "age": {YEAR: age},
                **({"tax_unit_role_input": {YEAR: role}} if role else {}),
            }
            for name, (age, role) in people.items()
        },
        "tax_units": {"tax_unit": {"members": list(people)}},
        "households": {"household": {"members": list(people)}},
    }


def test_supplied_input_carries_the_producers_column_name_and_values():
    """The role variable must match the column the Populace build writes.

    The loader sets a dataset column only when a variable has its exact name,
    and encodes a string column by Enum member name, so a renamed variable or
    member would silently drop the build's roles again. The build's filing
    status column must keep no variable of its name, so the model computes
    filing status rather than loading it.
    """
    role = system.variables["tax_unit_role_input"]
    assert role.entity.key == "person"
    assert not role.formulas  # An input, carried to every later year.
    assert role.default_value.name == "UNSPECIFIED"
    assert {"HEAD", "SPOUSE", "DEPENDENT"} <= set(role.possible_values.__members__)
    assert "filing_status_input" not in system.variables


@pytest.mark.parametrize(
    "people,message",
    [
        ({"head": (50, "HEAD"), "other": (20, None)}, "some members"),
        ({"head": (50, "HEAD"), "other": (20, "HEAD")}, "exactly one HEAD"),
        ({"only": (50, "DEPENDENT")}, "exactly one HEAD"),
        (
            {"head": (50, "HEAD"), "a": (45, "SPOUSE"), "b": (44, "SPOUSE")},
            "at most one",
        ),
    ],
    ids=["partly supplied", "two heads", "no head", "two spouses"],
)
def test_malformed_supplied_roles_raise(people, message):
    simulation = Simulation(situation=_situation(people))
    with pytest.raises(ValueError, match=message):
        simulation.calculate("is_tax_unit_head", YEAR)


def test_an_explicit_head_input_is_never_also_the_spouse():
    """Explicit role flags win over supplied roles without doubling a person."""
    situation = _situation({"a": (50, "HEAD"), "b": (48, "SPOUSE")})
    situation["people"]["b"]["is_tax_unit_head"] = {YEAR: True}
    simulation = Simulation(situation=situation)
    head = simulation.calculate("is_tax_unit_head", YEAR)
    spouse = simulation.calculate("is_tax_unit_spouse", YEAR)
    assert head.tolist() == [False, True]
    assert not (head & spouse).any()


def _dataset(
    with_supplied_roles: bool,
    filing_status_column: list | None = None,
    empty_tax_units: int = 0,
) -> USSingleYearDataset:
    """Three tax units in one household, with Populace-style string columns.

    1. A couple headed by a 30-year-old reference person with a 60-year-old
       spouse, and their 20-year-old full-time student.
    2. A 16-year-old living without a parent.
    3. A 50-year-old parent and their 21-year-old full-time student.

    ``empty_tax_units`` appends tax-unit rows that no person belongs to.
    """
    ages = [30, 60, 20, 16, 50, 21]
    tax_unit_of = [1, 1, 1, 2, 3, 3]
    person = pd.DataFrame(
        {
            "person_id": np.arange(1, 7),
            "person_household_id": np.ones(6, dtype=int),
            "person_tax_unit_id": tax_unit_of,
            "person_spm_unit_id": np.ones(6, dtype=int),
            "person_family_id": np.ones(6, dtype=int),
            "person_marital_unit_id": np.arange(1, 7),
            "age": np.asarray(ages, dtype=float),
            "is_full_time_student": [False, False, True, False, False, True],
        }
    )
    tax_unit = pd.DataFrame({"tax_unit_id": np.arange(1, 4 + empty_tax_units)})
    if with_supplied_roles:
        person["tax_unit_role_input"] = pd.array(
            ["HEAD", "SPOUSE", "DEPENDENT", "HEAD", "HEAD", "DEPENDENT"], dtype="str"
        )
    if filing_status_column is not None:
        tax_unit["filing_status_input"] = pd.array(filing_status_column, dtype="str")
    return USSingleYearDataset(
        person=person,
        household=pd.DataFrame(
            {"household_id": [1], "state_fips": [48], "household_weight": [1.0]}
        ),
        tax_unit=tax_unit,
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": np.arange(1, 7)}),
        time_period=YEAR,
    )


def _roles_and_statuses(simulation, year):
    return (
        np.asarray(simulation.calculate("is_tax_unit_head", year)).tolist(),
        np.asarray(simulation.calculate("is_tax_unit_spouse", year)).tolist(),
        np.asarray(simulation.calculate("is_tax_unit_dependent", year)).tolist(),
        np.asarray(simulation.calculate("filing_status", year)).tolist(),
    )


# The statuses the filing rules give the supplied roles: the couple files
# jointly, the lone 16-year-old is single, and the parent of a full-time
# student under 24 (a qualifying child, 26 USC 152(c)(3)(A)(ii)) is a head of
# household (26 USC 2(b)(1)(A)(i)).
COMPUTED_STATUSES = ["JOINT", "SINGLE", "HEAD_OF_HOUSEHOLD"]


@pytest.mark.parametrize("year", [YEAR, 2026])
def test_dataset_roles_hold_in_every_extended_year(year):
    simulation = Microsimulation(dataset=_dataset(True), dataset_end_year=2026)
    heads, spouses, dependents, statuses = _roles_and_statuses(simulation, year)
    assert heads == [True, False, False, True, True, False]
    assert spouses == [False, True, False, False, False, False]
    assert dependents == [False, False, True, False, False, True]
    assert statuses == COMPUTED_STATUSES


@pytest.mark.parametrize("year", [YEAR, 2026])
def test_a_supplied_filing_status_column_is_not_read(year):
    """Filing status is computed from the roles, whatever the build supplies.

    The column below disagrees with the filing rules for two units: it makes
    the lone 16-year-old a surviving spouse and the parent of a full-time
    student single. Neither holds; the rules decide.
    """
    dataset = _dataset(True, ["JOINT", "SURVIVING_SPOUSE", "SINGLE"])
    simulation = Microsimulation(dataset=dataset, dataset_end_year=2026)
    _, _, _, statuses = _roles_and_statuses(simulation, year)
    assert statuses == COMPUTED_STATUSES


def test_a_tax_unit_without_members_falls_back_rather_than_raising():
    """A tax-unit row that no person belongs to supplies no roles.

    The loader declares every tax unit in the dataset's id column, members or
    not, and ``all`` over no members is True. Such a unit must fall back to
    age ordering, which gives it no head, as before supplied roles existed,
    rather than count as supplied with no HEAD and raise.
    """
    dataset = _dataset(True, empty_tax_units=1)
    simulation = Microsimulation(dataset=dataset, dataset_end_year=YEAR)
    supplied = simulation.calculate("tax_unit_roles_supplied", YEAR, use_weights=False)
    assert np.asarray(supplied).tolist() == [True, True, True, False]
    heads = simulation.calculate("is_tax_unit_head", YEAR, use_weights=False)
    spouses = simulation.calculate("is_tax_unit_spouse", YEAR, use_weights=False)
    assert np.asarray(heads).tolist() == [True, False, False, True, True, False]
    assert np.asarray(spouses).tolist() == [False, True, False, False, False, False]


def test_dataset_without_supplied_columns_keeps_age_ordering():
    """The same people without the columns: the oldest adult heads each unit.

    The 60-year-old heads the couple, the 16-year-old heads nothing, and the
    student becomes the parent's spouse, so both multi-person units file
    jointly - the behaviour the supplied roles exist to correct.
    """
    simulation = Microsimulation(dataset=_dataset(False), dataset_end_year=YEAR)
    heads, spouses, dependents, statuses = _roles_and_statuses(simulation, YEAR)
    assert heads == [False, True, False, False, True, False]
    assert spouses == [True, False, False, False, False, True]
    assert dependents == [False, False, True, True, False, False]
    assert statuses == ["JOINT", "HEAD_OF_HOUSEHOLD", "JOINT"]
