"""Structural guards for the SNAP ABAWD waived-area list parameters.

is_in_snap_abawd_waived_area matches each waived_counties/<state>.yaml entry
against county_str (the County enum name) with np.isin, only for households
whose state_code equals the file stem, and matches waived_states entries
against state_code. A misspelled entry, or one filed under the wrong state,
therefore never matches and fails silently. The New Mexico entry for Dona Ana
County is the likeliest case: its County enum name contains a precomposed
N-tilde (U+00D1), so an ASCII or decomposed spelling would drop the county.
"""

from pathlib import Path

import pytest
import yaml

from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)

ABAWD = (
    Path(__file__).parent.parent
    / "parameters"
    / "gov"
    / "usda"
    / "snap"
    / "work_requirements"
    / "abawd"
)
WAIVED_COUNTIES = ABAWD / "waived_counties"
WAIVED_STATES = ABAWD / "waived_states.yaml"
COUNTY_FILES = sorted(WAIVED_COUNTIES.glob("*.yaml"))


def list_entries(path):
    # Read as UTF-8 explicitly: the platform default (cp1252 on Windows)
    # would mangle the non-ASCII Dona Ana County, NM enum name.
    raw = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    return sorted(
        {
            entry
            for entries in raw["values"].values()
            if isinstance(entries, list)
            for entry in entries
        }
    )


def test_waived_county_files_are_found():
    assert COUNTY_FILES, f"No waived_counties files found under {WAIVED_COUNTIES}"


@pytest.mark.parametrize("path", COUNTY_FILES, ids=lambda path: path.stem)
def test_waived_county_file_is_named_for_a_state(path):
    assert path.stem == path.stem.lower() and path.stem.upper() in (
        StateCode.__members__
    ), (
        f"{path.name} must be named for a lowercase state code; the formula "
        "gates each list on state_code == file stem upper-cased."
    )


@pytest.mark.parametrize("path", COUNTY_FILES, ids=lambda path: path.stem)
def test_waived_counties_are_county_enum_names_in_the_file_state(path):
    suffix = f"_{path.stem.upper()}"
    not_in_enum = [
        entry for entry in list_entries(path) if entry not in County.__members__
    ]
    wrong_state = [entry for entry in list_entries(path) if not entry.endswith(suffix)]
    assert not not_in_enum, (
        f"{path.name} lists names that are not County enum members, so they "
        f"never match county_str: {not_in_enum}"
    )
    assert not wrong_state, (
        f"{path.name} lists counties without the {suffix} suffix, so they "
        f"belong to another state and never match: {wrong_state}"
    )


def test_waived_states_are_state_codes():
    not_state_codes = [
        entry
        for entry in list_entries(WAIVED_STATES)
        if entry not in StateCode.__members__
    ]
    assert not not_state_codes, (
        "waived_states.yaml lists entries that are not StateCode members, so "
        f"they never match state_code: {not_state_codes}"
    )
