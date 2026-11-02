"""Let ``state_fips`` decide which state a dataset's household lives in.

A microdata file can place a household through several columns, and a run can
change only one of them: a simulated instrument keeps each family and sets
``state_fips`` to one state after another. What the file still says about the
old state would then contradict it. Reading those columns as they stand gives
the wrong rules without saying so (a county's SPM threshold with another state's
taxes, or a stored ``state_code`` that keeps the old state altogether) or crashes
a county-keyed parameter lookup.

So ``state_fips`` wins. A state label that disagrees takes the value
``state_fips`` implies, and local geography that sits outside the state becomes
unknown for that household, as if the file had never given it. A logged warning
says so, because the same contradiction can also mean a damaged file. Each year
answers for what it reads, including what it carries from another year: a
county stored for 2024 still sits in 2025 when ``state_fips`` changes between
them.
"""

from functools import lru_cache
import logging

import numpy as np
import pandas as pd

from policyengine_us.model_api import STATES
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us.variables.household.demographic.geographic.county.first_county_in_state import (
    first_county_by_state,
)
from policyengine_us.variables.household.demographic.geographic.state_name import (
    STATE_NAME_BY_FIPS,
)

STATE_LABELS = ("state_code", "state_name", "state_code_str")
GEOID_LENGTHS = {"county_fips": 5, "tract_geoid": 11, "block_geoid": 15}
COUNTY_NAMES = ("county", "county_str")
# Local geography that names its state, and so can contradict state_fips.
STATE_NAMING_GEOGRAPHY = (
    *GEOID_LENGTHS,
    *COUNTY_NAMES,
    "congressional_district_geoid",
)
# Values tied to a place that do not name its state. These cannot contradict
# state_fips on their own, and go with the columns above when they do.
OTHER_LOCAL_GEOGRAPHY = (
    "average_home_energy_use_in_state",
    "cbsa_code",
    "place_fips",
    "puma",
    "sldl",
    "sldu",
    "vtd",
    "zcta",
    "zip_code",
)
# A stored value hides its variable's formula, so a stored copy of what the
# model derives from local geography goes with that geography, and one of what
# it derives from the state goes whenever state_fips is in force.
DERIVED_FROM_LOCAL_GEOGRAPHY = (
    "in_ny_mctd_zone_2",
    "in_nyc",
    "medicaid_rating_area",
    "three_digit_zip_code",
)
DERIVED_FROM_STATE = (
    *STATES,
    "spm_unit_state_fips",
    "state_group",
    "state_group_str",
    "tax_unit_state",
)

NO_STATE = 0
STATE_CODE_BY_FIPS = {fips: name.name for fips, name in STATE_NAME_BY_FIPS.items()}
FIPS_BY_STATE_CODE = {code: fips for fips, code in STATE_CODE_BY_FIPS.items()}
STATE_CODE_LOOKUP = np.full(max(STATE_CODE_BY_FIPS) + 1, "", dtype=object)
STATE_CODE_LOOKUP[list(STATE_CODE_BY_FIPS)] = list(STATE_CODE_BY_FIPS.values())


def _stored(simulation, name):
    """Map each period of ``name`` to the array this simulation stores for it."""
    holder = simulation.get_holder(name)
    arrays = {}
    for period in holder.get_known_periods():
        array = holder.get_array(period, simulation.branch_name)
        if array is not None:
            arrays[period] = array
    return arrays


def _as_text(values):
    """Enum names or stored strings as an object array of ``str``."""
    if hasattr(values, "decode_to_str"):
        values = values.decode_to_str()
    return np.array(
        [value.decode() if isinstance(value, bytes) else value for value in values],
        dtype=object,
    )


def _in_force(arrays, period):
    """The array ``period`` reads from ``arrays``, carried forward."""
    if period in arrays:
        return arrays[period]
    earlier = [known for known in arrays if known.start <= period.start]
    if earlier:
        return arrays[max(earlier, key=lambda known: known.start)]
    return None


def _read_at(name, arrays, period):
    """The stored array ``period`` reads for the variable ``name``, if any."""
    if name == "county" and arrays and period not in arrays:
        # Its formula takes the latest stored county, whichever year that is.
        return arrays[max(arrays, key=lambda known: known.start)]
    return _in_force(arrays, period)


def _geoid_text(value, length):
    """``value`` as GEOID text, with the leading zeros a number loses."""
    if isinstance(value, bytes):
        value = value.decode()
    if pd.isna(value):
        return ""
    text = str(value).removesuffix(".0")
    return text.zfill(length) if text.isdigit() else text


def _is_geoid(value, length):
    """Whether ``value`` is a complete GEOID: digits, as text, at full length."""
    return isinstance(value, str) and len(value) == length and value.isdigit()


def _state_named_by(name, value):
    """The state FIPS code a stored value names, or ``NO_STATE`` if none."""
    if name in COUNTY_NAMES:
        if isinstance(value, bytes):
            value = value.decode()
        if not isinstance(value, str):
            return NO_STATE
        # "LOS_ANGELES_COUNTY_CA" names California; "UNKNOWN" names nothing.
        return FIPS_BY_STATE_CODE.get(value.rsplit("_", 1)[-1], NO_STATE)
    geoid = _geoid_text(value, GEOID_LENGTHS[name])
    return int(geoid[:2]) if _is_geoid(geoid, GEOID_LENGTHS[name]) else NO_STATE


def _outside_state(name, values, state):
    """Whether each household's stored value sits outside its state."""
    if name == "congressional_district_geoid":
        values = np.asarray(values)
        return (values > 0) & (values // 100 != state)
    if hasattr(values, "decode_to_str"):
        values = values.decode_to_str()
    codes, distinct = pd.factorize(
        np.asarray(values, dtype=object), use_na_sentinel=False
    )
    named = np.array([_state_named_by(name, value) for value in distinct])[codes]
    return (named != NO_STATE) & (named != state)


def _align_state_labels(simulation, states):
    """Overwrite stored state labels that disagree with ``state_fips``."""
    corrected = set()
    for name in STATE_LABELS:
        for period, values in _stored(simulation, name).items():
            state = _in_force(states, period)
            if state is None:
                continue
            expected = STATE_CODE_LOOKUP[state]
            if (_as_text(values) != expected).any():
                simulation.set_input(name, period, expected)
                corrected.add(name)
    return corrected


def _drop_stored_state_results(simulation, states):
    """Remove stored copies of what the model derives from the state."""
    for name in DERIVED_FROM_STATE:
        for period in _stored(simulation, name):
            if _in_force(states, period) is not None:
                simulation.get_holder(name).delete_arrays(
                    period, simulation.branch_name
                )


def _forget_local_geography(simulation, period, outside, state):
    """Reset each household's local geography to unknown where ``outside``."""
    first_counties = first_county_by_state()
    for name in (*STATE_NAMING_GEOGRAPHY, *OTHER_LOCAL_GEOGRAPHY):
        values = _read_at(name, _stored(simulation, name), period)
        if values is None:
            continue
        if name in COUNTY_NAMES:
            # A stored county overrides the formula's fallback, so it takes
            # that fallback's value itself.
            replaced = _as_text(values)
            replaced[outside] = [
                first_counties.get(code, County.UNKNOWN).name
                for code in STATE_CODE_LOOKUP[state[outside]]
            ]
        else:
            variable = simulation.tax_benefit_system.get_variable(name)
            if variable.value_type is str:
                replaced = _as_text(values)
            else:
                replaced = np.array(values, copy=True)
            replaced[outside] = variable.default_value
        simulation.set_input(name, period, replaced)
    for name in DERIVED_FROM_LOCAL_GEOGRAPHY:
        simulation.get_holder(name).delete_arrays(period, simulation.branch_name)


def _reconcile(simulation, states):
    """Apply ``state_fips`` to one simulation and report what changed."""
    corrected_labels = _align_state_labels(simulation, states)
    _drop_stored_state_results(simulation, states)
    forgotten = {}
    conflicting = set()
    periods = sorted(
        {
            *states,
            *(
                period
                for name in STATE_NAMING_GEOGRAPHY
                for period in _stored(simulation, name)
            ),
        },
        key=lambda period: period.start,
    )
    for period in periods:
        state = _in_force(states, period)
        if state is None:
            continue
        outside = np.zeros(len(state), dtype=bool)
        for name in STATE_NAMING_GEOGRAPHY:
            values = _read_at(name, _stored(simulation, name), period)
            if values is not None:
                contradicts = _outside_state(name, values, state)
                if contradicts.any():
                    conflicting.add(name)
                outside |= contradicts
        if outside.any():
            _forget_local_geography(simulation, period, outside, state)
            forgotten[period] = int(outside.sum())
    return corrected_labels, conflicting, forgotten


def _span(periods):
    """Name a run of periods compactly: ``2024`` or ``2024 to 2036``."""
    ordered = sorted(str(period) for period in periods)
    return ordered[0] if len(ordered) == 1 else f"{ordered[0]} to {ordered[-1]}"


def _warn_if_state_changes_between_years(states):
    """Say when a household's state differs between a dataset's years."""
    ordered = sorted(states, key=lambda period: period.start)
    changes = sum(
        np.asarray(states[earlier]) != np.asarray(states[later])
        for earlier, later in zip(ordered, ordered[1:])
    )
    if np.any(changes):
        logging.warning(
            f"state_fips changes between {_span(ordered)} for "
            f"{int(np.count_nonzero(changes)):,} household(s). Each year reads "
            "its own column, so a state set for one year leaves the others as "
            "they were."
        )


@lru_cache(maxsize=1)
def _known_county_fips():
    return frozenset(load_county_fips_dataset()["county_fips"])


def _warn_about_county_codes(simulation):
    """Say when ``county_fips`` cannot give a household its county."""
    for values in _stored(simulation, "county_fips").values():
        held = {
            value.decode() if isinstance(value, bytes) else value
            for value in pd.unique(np.asarray(values, dtype=object))
            if not pd.isna(value) and value != ""
        }
        text = {value for value in held if isinstance(value, str)}
        if text != held:
            logging.warning(
                "county_fips holds numbers, not five-digit text. County-keyed "
                "rules use the first county in the state for any code that lost "
                "a leading zero, and county SPM thresholds refuse the column. "
                'Read it as text, for example read_csv(..., dtype={"county_fips": '
                "str})."
            )
            return
        unknown = text - _known_county_fips() if text else text
        if unknown:
            logging.warning(
                f"county_fips holds {len(unknown):,} code(s) that name no county, "
                f"such as {min(unknown)}, so those households use the first "
                "county in their state for county-keyed rules."
            )
            return


def reconcile_geography_with_state(simulation):
    """Make a dataset simulation's geography agree with its ``state_fips``.

    Call this once the dataset has loaded, and before anything is calculated.
    A reform's baseline gets the same treatment. Geography the reconciliation
    rewrites stays recorded as an input, so an export of the simulation holds it.
    """
    if not simulation.is_over_dataset:
        return
    _warn_about_county_codes(simulation)
    states = _stored(simulation, "state_fips")
    if not states:
        return
    unknown = set(np.unique(np.concatenate(list(states.values())))) - set(
        STATE_CODE_BY_FIPS
    )
    if unknown:
        raise ValueError(
            f"state_fips holds code(s) this model has no state for: "
            f"{', '.join(str(code) for code in sorted(unknown))}. It covers the "
            "50 states, DC and Puerto Rico."
        )
    _warn_if_state_changes_between_years(states)

    corrected_labels, conflicting, forgotten = _reconcile(simulation, states)
    baseline = simulation.baseline
    if baseline is not None and baseline is not simulation:
        _reconcile(baseline, _stored(baseline, "state_fips"))

    if corrected_labels:
        logging.warning(
            f"The dataset's {', '.join(sorted(corrected_labels))} disagreed with "
            "state_fips, so state_fips decided each household's state."
        )
    if forgotten:
        households = len(next(iter(states.values())))
        logging.warning(
            f"state_fips puts up to {max(forgotten.values()):,} of {households:,} "
            f"household(s) outside the {', '.join(sorted(conflicting))} read "
            f"for {_span(forgotten)}. That local geography is unknown for those "
            "households, so county-keyed rules use the first county in the "
            'state, and SPM thresholds need spm={"geography_kind": "national"}.'
        )
