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
says so, because the same contradiction can also mean a damaged file.
"""

import logging

import numpy as np
import pandas as pd

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
# Local geography that does not name its state. It cannot contradict state_fips
# on its own, and goes with the columns above when they do.
OTHER_LOCAL_GEOGRAPHY = (
    "cbsa_code",
    "place_fips",
    "puma",
    "sldl",
    "sldu",
    "vtd",
    "zcta",
    "zip_code",
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


def _state_at(states, period):
    """The ``state_fips`` array in force at ``period``, carried forward."""
    if period in states:
        return states[period]
    earlier = [known for known in states if known.start <= period.start]
    if earlier:
        return states[max(earlier, key=lambda known: known.start)]
    return None


def _is_geoid(value, length):
    """Whether ``value`` is a complete GEOID: digits, as text, at full length."""
    return isinstance(value, str) and len(value) == length and value.isdigit()


def _state_named_by(name, value):
    """The state FIPS code a stored value names, or ``NO_STATE`` if none."""
    if isinstance(value, bytes):
        value = value.decode()
    if not isinstance(value, str):
        return NO_STATE
    if name in COUNTY_NAMES:
        # "LOS_ANGELES_COUNTY_CA" names California; "UNKNOWN" names nothing.
        return FIPS_BY_STATE_CODE.get(value.rsplit("_", 1)[-1], NO_STATE)
    if _is_geoid(value, GEOID_LENGTHS[name]):
        return int(value[:2])
    return NO_STATE


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
            state = _state_at(states, period)
            if state is None:
                continue
            expected = STATE_CODE_LOOKUP[state]
            if (_as_text(values) != expected).any():
                simulation.set_input(name, period, expected)
                corrected.add(name)
    return corrected


def _forget_local_geography(simulation, period, outside, state):
    """Reset each household's local geography to unknown where ``outside``."""
    first_counties = first_county_by_state()
    for name in (*STATE_NAMING_GEOGRAPHY, *OTHER_LOCAL_GEOGRAPHY):
        values = _stored(simulation, name).get(period)
        if values is None:
            continue
        variable = simulation.tax_benefit_system.get_variable(name)
        if variable.value_type is int:
            replaced = np.array(values, copy=True)
        else:
            replaced = _as_text(values)
        if name in COUNTY_NAMES:
            # A stored county overrides the formula's fallback, so it takes
            # that fallback's value itself.
            replaced[outside] = [
                first_counties.get(code, County.UNKNOWN).name
                for code in STATE_CODE_LOOKUP[state[outside]]
            ]
        else:
            replaced[outside] = variable.default_value
        simulation.set_input(name, period, replaced)


def _reconcile(simulation, states):
    """Apply ``state_fips`` to one simulation and report what changed."""
    corrected_labels = _align_state_labels(simulation, states)
    forgotten = {}
    conflicting = set()
    periods = sorted(
        {
            period
            for name in STATE_NAMING_GEOGRAPHY
            for period in _stored(simulation, name)
        },
        key=lambda period: period.start,
    )
    for period in periods:
        state = _state_at(states, period)
        if state is None:
            continue
        outside = np.zeros(len(state), dtype=bool)
        for name in STATE_NAMING_GEOGRAPHY:
            values = _stored(simulation, name).get(period)
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


def _warn_if_county_is_malformed(simulation):
    """Say when ``county_fips`` lost its leading zero, as ``read_csv`` leaves it."""
    for values in _stored(simulation, "county_fips").values():
        distinct = pd.unique(np.asarray(values, dtype=object))
        decoded = [
            value.decode() if isinstance(value, bytes) else value for value in distinct
        ]
        if not all(
            value == "" or _is_geoid(value, GEOID_LENGTHS["county_fips"])
            for value in decoded
        ):
            logging.warning(
                "county_fips holds values other than five-digit text, so "
                "county-keyed rules use the first county in those states. Read "
                'the column as text, for example read_csv(..., dtype={"county_fips": '
                "str})."
            )
            return


def reconcile_geography_with_state(simulation):
    """Make a dataset simulation's geography agree with its ``state_fips``.

    Call this once the dataset has loaded, and before anything is calculated.
    A reform's baseline gets the same treatment. The input stays recorded as an
    input, so an export of the simulation holds the reconciled geography.
    """
    if not simulation.is_over_dataset:
        return
    _warn_if_county_is_malformed(simulation)
    states = _stored(simulation, "state_fips")
    if not states:
        return
    unknown = set(np.unique(np.concatenate(list(states.values())))) - set(
        STATE_CODE_BY_FIPS
    )
    if unknown:
        raise ValueError(
            f"state_fips holds code(s) that name no state: "
            f"{', '.join(str(code) for code in sorted(unknown))}."
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
            f"household(s) outside the {', '.join(sorted(conflicting))} stored "
            f"for {_span(forgotten)}. That local geography is unknown for those "
            "households, so county-keyed rules use the first county in the "
            'state, and SPM thresholds need spm={"geography_kind": "national"}.'
        )
