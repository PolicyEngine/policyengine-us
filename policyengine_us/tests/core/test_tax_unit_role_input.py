"""Tax-unit roles and filing statuses supplied by a population dataset.

The Populace US build's tax-unit constructor (microunit, called from
microcosm-frame) assigns every person a role - HEAD, SPOUSE or DEPENDENT - and
every tax unit a filing status, and writes them to the person column
``tax_unit_role_input`` and the tax-unit column ``filing_status_input``. The
role variables and ``filing_status`` use them when supplied and fall back to
age ordering and the filing rules when not.

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
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)

YEAR = 2024


def _situation(people: dict, filing_status_input: str | None = None) -> dict:
    tax_unit = {"members": list(people)}
    if filing_status_input is not None:
        tax_unit["filing_status_input"] = {YEAR: filing_status_input}
    return {
        "people": {
            name: {
                "age": {YEAR: age},
                **({"tax_unit_role_input": {YEAR: role}} if role else {}),
            }
            for name, (age, role) in people.items()
        },
        "tax_units": {"tax_unit": tax_unit},
        "households": {"household": {"members": list(people)}},
    }


def test_supplied_inputs_carry_the_producers_column_names_and_values():
    """The variables must match the columns the Populace build writes.

    The loader sets a dataset column only when a variable has its exact name,
    and encodes a string column by Enum member name, so a renamed variable or
    member would silently drop the build's roles again.
    """
    role = system.variables["tax_unit_role_input"]
    status = system.variables["filing_status_input"]
    assert role.entity.key == "person"
    assert status.entity.key == "tax_unit"
    for variable in (role, status):
        assert not variable.formulas  # An input, carried to every later year.
        assert variable.default_value.name == "UNSPECIFIED"
    assert {"HEAD", "SPOUSE", "DEPENDENT"} <= set(role.possible_values.__members__)
    # Every status the rules can derive can also be supplied.
    assert set(status.possible_values.__members__) == {
        "UNSPECIFIED",
        *FilingStatus.__members__,
    }


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


@pytest.mark.parametrize(
    "people,status",
    [
        ({"head": (50, "HEAD")}, "JOINT"),
        ({"head": (50, "HEAD"), "spouse": (48, "SPOUSE")}, "SINGLE"),
        ({"older": (50, None), "younger": (48, None)}, "HEAD_OF_HOUSEHOLD"),
    ],
    ids=["joint without a spouse", "spouse but not joint", "age-rule spouse"],
)
def test_supplied_status_must_agree_with_the_units_spouse(people, status):
    simulation = Simulation(situation=_situation(people, status))
    with pytest.raises(ValueError, match="filing_status_input disagrees"):
        simulation.calculate("filing_status", YEAR)


def _abolish(variable: str) -> dict:
    return {f"gov.abolitions.{variable}": {"2000-01-01.2100-12-31": True}}


@pytest.mark.parametrize(
    "status,abolished,expected",
    [
        ("HEAD_OF_HOUSEHOLD", "head_of_household_eligible", "SINGLE"),
        ("SINGLE", "head_of_household_eligible", "SINGLE"),
        ("SURVIVING_SPOUSE", "surviving_spouse_eligible", "HEAD_OF_HOUSEHOLD"),
        ("HEAD_OF_HOUSEHOLD", "surviving_spouse_eligible", "HEAD_OF_HOUSEHOLD"),
    ],
    ids=[
        "abolished HOH re-derives a supplied HOH",
        "abolished HOH keeps a supplied SINGLE",
        "abolished SS re-derives a supplied SS",
        "abolished SS keeps a supplied HOH",
    ],
)
def test_abolishing_a_status_rule_re_derives_only_that_status(
    status, abolished, expected
):
    """A parent of a 10-year-old, supplied with a status the rules may not give.

    Abolishing an eligibility rule removes that status, so a unit supplied with
    it is re-derived from the remaining rules; a unit supplied with another
    status keeps it, as the rules would not otherwise differ from the input.
    """
    people = {"parent": (40, "HEAD"), "child": (10, "DEPENDENT")}
    simulation = Simulation(
        situation=_situation(people, status), reform=_abolish(abolished)
    )
    assert simulation.calculate("filing_status", YEAR).decode_to_str().tolist() == [
        expected
    ]


@pytest.mark.parametrize(
    "abolished", ["tax_unit_married", "is_tax_unit_spouse", "tax_unit_roles_supplied"]
)
def test_abolishing_a_role_variable_does_not_fail_the_status_check(abolished):
    """The JOINT check reads the supplied roles, not the abolishable variables."""
    people = {"head": (40, "HEAD"), "spouse": (40, "SPOUSE")}
    simulation = Simulation(
        situation=_situation(people, "JOINT"), reform=_abolish(abolished)
    )
    assert simulation.calculate("filing_status", YEAR).decode_to_str().tolist() == [
        "JOINT"
    ]


def test_an_explicit_head_input_is_never_also_the_spouse():
    """Explicit role flags win over supplied roles without doubling a person."""
    situation = _situation({"a": (50, "HEAD"), "b": (48, "SPOUSE")})
    situation["people"]["b"]["is_tax_unit_head"] = {YEAR: True}
    simulation = Simulation(situation=situation)
    head = simulation.calculate("is_tax_unit_head", YEAR)
    spouse = simulation.calculate("is_tax_unit_spouse", YEAR)
    assert head.tolist() == [False, True]
    assert not (head & spouse).any()


def _dataset(with_supplied_columns: bool) -> USSingleYearDataset:
    """Three tax units in one household, with Populace-style string columns.

    1. A couple headed by a 30-year-old reference person with a 60-year-old
       spouse, and their 20-year-old full-time student.
    2. A 16-year-old living without a parent.
    3. A 50-year-old parent and their 21-year-old full-time student.
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
    tax_unit = pd.DataFrame({"tax_unit_id": [1, 2, 3]})
    if with_supplied_columns:
        person["tax_unit_role_input"] = pd.array(
            ["HEAD", "SPOUSE", "DEPENDENT", "HEAD", "HEAD", "DEPENDENT"], dtype="str"
        )
        tax_unit["filing_status_input"] = pd.array(
            ["JOINT", "SINGLE", "HEAD_OF_HOUSEHOLD"], dtype="str"
        )
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


@pytest.mark.parametrize("year", [YEAR, 2026])
def test_dataset_roles_and_statuses_hold_in_every_extended_year(year):
    simulation = Microsimulation(dataset=_dataset(True), dataset_end_year=2026)
    heads, spouses, dependents, statuses = _roles_and_statuses(simulation, year)
    assert heads == [True, False, False, True, True, False]
    assert spouses == [False, True, False, False, False, False]
    assert dependents == [False, False, True, False, False, True]
    assert statuses == ["JOINT", "SINGLE", "HEAD_OF_HOUSEHOLD"]


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
