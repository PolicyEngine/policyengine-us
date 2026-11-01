"""Structural guards for the SNAP ABAWD waived-area list parameters.

is_in_snap_abawd_waived_area matches each waived_counties/<state>.yaml entry
against county_str (the County enum name) with np.isin, only for households
whose state_code equals the file stem, and matches waived_states entries
against state_code. A misspelled entry, or one filed under the wrong state,
therefore never matches and fails silently. The New Mexico entry for Dona Ana
County is the likeliest case: its County enum name contains a precomposed
N-tilde (U+00D1), so an ASCII or decomposed spelling would drop the county.

The lists are also dated. A duplicate date key silently keeps only the last
list (PyYAML's default behavior), and a scalar where a list belongs would
break np.isin, so both are rejected here. Finally, the pre-P.L. 119-21
snapshot date in the variable must stay one day before the
hr1_waiver_criteria switch turns on.
"""

import datetime
import re
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

from policyengine_us.variables.gov.usda.snap.eligibility.work_requirements.is_in_snap_abawd_waived_area import (
    PRE_HR1_WAIVER_SNAPSHOT,
)
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
HR1_WAIVER_CRITERIA_IN_EFFECT = ABAWD / "hr1_waiver_criteria" / "in_effect.yaml"
COUNTY_FILES = sorted(WAIVED_COUNTIES.glob("*.yaml"))
LIST_FILES = COUNTY_FILES + [WAIVED_STATES]
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class UniqueKeyLoader(yaml.BaseLoader):
    """BaseLoader that rejects duplicate mapping keys instead of keeping the
    last one. BaseLoader keeps every scalar as a string, so date keys such as
    0000-01-01 load without date parsing."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None,
                    None,
                    f"duplicate key {key!r}",
                    key_node.start_mark,
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


@lru_cache(maxsize=None)
def load(path):
    # Read as UTF-8 explicitly: the platform default (cp1252 on Windows)
    # would mangle the non-ASCII Dona Ana County, NM enum name.
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def list_entries(path):
    return sorted(
        {
            entry
            for entries in load(path)["values"].values()
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


@pytest.mark.parametrize("path", LIST_FILES, ids=lambda path: path.stem)
def test_waived_list_date_keys_are_iso_ascending_and_unique(path):
    # Duplicate keys raise in UniqueKeyLoader.
    keys = list(load(path)["values"])
    not_iso = [key for key in keys if not ISO_DATE.fullmatch(key)]
    assert not not_iso, f"{path.name} has non-ISO date keys: {not_iso}"
    for key in keys:
        datetime.date.fromisoformat(key)
    out_of_order = [
        (earlier, later) for earlier, later in zip(keys, keys[1:]) if earlier >= later
    ]
    assert not out_of_order, (
        f"{path.name} date keys must be strictly ascending: {out_of_order}"
    )


@pytest.mark.parametrize("path", LIST_FILES, ids=lambda path: path.stem)
def test_waived_list_values_are_lists(path):
    scalars = {
        key: value
        for key, value in load(path)["values"].items()
        if not isinstance(value, list)
    }
    assert not scalars, (
        f"{path.name} has non-list values, which np.isin would treat as a "
        f"single entry or reject: {scalars}"
    )


@pytest.mark.parametrize("path", COUNTY_FILES, ids=lambda path: path.stem)
def test_waived_counties_are_county_enum_names_in_the_file_state(path):
    suffix = f"_{path.stem.upper()}"
    entries = list_entries(path)
    not_in_enum = [entry for entry in entries if entry not in County.__members__]
    wrong_state = [entry for entry in entries if not entry.endswith(suffix)]
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


def test_pre_hr1_waiver_snapshot_is_the_day_before_the_switch_turns_on():
    # BaseLoader keeps values as strings; safe_load cannot parse 0000-01-01.
    values = load(HR1_WAIVER_CRITERIA_IN_EFFECT)["values"]
    first_true = min(key for key, value in values.items() if value == "true")
    day_before = datetime.date.fromisoformat(first_true) - datetime.timedelta(days=1)
    assert day_before == datetime.date.fromisoformat(PRE_HR1_WAIVER_SNAPSHOT), (
        f"PRE_HR1_WAIVER_SNAPSHOT ({PRE_HR1_WAIVER_SNAPSHOT}) must be the day "
        f"before hr1_waiver_criteria.in_effect first turns true ({first_true})."
    )
