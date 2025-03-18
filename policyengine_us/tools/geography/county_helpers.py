import pandas as pd
import numpy as np
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


def map_county_string_to_enum(
    county_name: "pd.Series[str]", state_code: "pd.Series[str]"
) -> "pd.Series[int]":
    """Helper function to map county name and state code to County enum value."""
    county_key = county_name.apply(
        lambda name: name.replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
        .replace("'", "_")
        .strip()
        .upper()
    )
    county_state = county_key.str.cat(state_code, sep="_")
    county_names = pd.Series(
        np.arange(len(County._member_names_)),
        index=County._member_names_,
    )
    return county_names[county_state]
