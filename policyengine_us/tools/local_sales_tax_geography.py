"""Resolve household geography consistently for the local sales tax lookups."""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    map_county_string_to_enum,
    state_fips_by_state_code,
)
from policyengine_us.tools.local_sales_tax_rates import locality_place_counties
from policyengine_us.tools.period_branch import _input_keys, _is_known


@dataclass(frozen=True)
class SalesTaxLocation:
    state_code: pd.Series
    county_fips: pd.Series
    place_fips: pd.Series
    place_geoid: pd.Series
    block_known: pd.Series


def _stored_input(simulation, holder, period, keys):
    """Whether the first readable stored value is a supplied input."""
    name = holder.variable.name
    for branch in simulation._get_visible_branch_names():
        if holder._get_array_from_storage(period, branch) is None:
            continue
        # Match get_array's first live branch: a nearer calculated cache
        # must not acquire the provenance of an ancestor's supplied input.
        if (name, branch, period) not in keys:
            return False
        # Newer Core also distinguishes a cache write that replaced an input
        # at the same key. The registry and exact stored value are available
        # throughout the supported Core versions.
        is_input = getattr(holder, "_is_input", None)
        if is_input is not None and not is_input(period, branch):
            return False
        return True
    return False


def _supplied_input(household, period, name):
    """Read supplied values without treating calculated defaults as inputs.

    Core >= 3.32.27 records supplied inputs and the branch ancestry. Access
    the variable through the household as well so Core tracks the formula's
    dependency, including when an input is supplied after this calculation.
    """
    simulation = household.simulation
    holder = simulation.get_holder(name)
    values = household(name, period)
    # Yonkers has no formula and defaults to false: a true value comes from
    # an entered flag, including Core's carryover of an earlier year's input.
    if not holder.variable.formulas:
        return values
    keys = _input_keys(simulation)
    if _stored_input(simulation, holder, period, keys):
        return values
    if name == "county" and simulation.is_over_dataset:
        # The county formula carries stored county data into later dataset
        # years. Core caches that result as calculated, not as a new input.
        # A calculated value shadowing an input for this year still wins.
        if any(
            key_name == name and key_period == period
            for key_name, _, key_period in keys
        ):
            return None
        source_periods = sorted(
            {
                p
                for key_name, _, p in keys
                if key_name == name and p.start < period.start
            },
            key=lambda p: (p.start, p.stop, str(p)),
            reverse=True,
        )
        for source_period in source_periods:
            if not _is_known(simulation, name, source_period):
                continue
            if not _stored_input(simulation, holder, source_period, keys):
                return None
            supplied = household(name, source_period)
            return values if np.array_equal(values, supplied) else None
    return None


@lru_cache(maxsize=None)
def _county_fips_by_enum():
    counties = load_county_fips_dataset()
    enum = map_county_string_to_enum(counties["county_name"], counties["state"])
    # UNKNOWN has enum index 0 and must never become a geographic signal.
    return pd.Series(counties["county_fips"].to_numpy(), index=enum).loc[
        lambda values: (values.index != 0) & ~values.index.duplicated()
    ]


@lru_cache(maxsize=None)
def _county_fips_codes():
    return pd.Index(load_county_fips_dataset()["county_fips"])


def sales_tax_location(household, period):
    state = pd.Series(household("state_code_str", period)).astype(str)
    state_fips = state.map(state_fips_by_state_code()).fillna("")
    county = pd.Series(household("county_fips", period)).astype(str)
    county = county.where(county.str.fullmatch(r"\d{1,5}"), "").str.zfill(5)
    valid_counties = _county_fips_codes()
    county = county.where(
        (county.str[:2] == state_fips) & county.isin(valid_counties), ""
    )
    block = pd.Series(household("block_geoid", period)).astype(str)
    block_known = (
        block.str.fullmatch(r"\d{15}")
        & (block.str[:2] == state_fips)
        & block.str[:5].isin(valid_counties)
    )
    county = county.where(county != "", block.str[:5].where(block_known, ""))

    if (county == "").any():
        supplied_county = _supplied_input(household, period, "county")
        if supplied_county is not None:
            enum_county = (
                pd.Series(np.asarray(supplied_county))
                .map(_county_fips_by_enum())
                .fillna("")
            )
            enum_county = enum_county.where(enum_county.str[:2] == state_fips, "")
            county = county.where(county != "", enum_county)

    place = pd.Series(household("place_fips", period)).astype(str)
    is_geoid = place.str.fullmatch(r"\d{7}")
    geoid_in_state = is_geoid & (place.str[:2] == state_fips)
    # Keep the state prefix long enough to reject an out-of-state GEOID.
    place = place.where(~is_geoid, place.str[2:].where(geoid_in_state, ""))
    place = place.where(place.str.fullmatch(r"\d{1,5}"), "").str.zfill(5)
    place = place.where(place != "00000", "")
    for flag, code in (("in_nyc", "51000"), ("in_yonkers", "84000")):
        if ((place == "") & (state == "NY")).any():
            supplied_flag = _supplied_input(household, period, flag)
            if supplied_flag is not None:
                inferred = (place == "") & (state == "NY") & supplied_flag
                place = place.where(~inferred, code)
    place_geoid = (state_fips + place).where(place != "", "")
    missing_county = county == ""
    if missing_county.any():
        county.loc[missing_county] = (
            place_geoid[missing_county].map(locality_place_counties()).fillna("")
        )
    return SalesTaxLocation(state, county, place, place_geoid, block_known)
