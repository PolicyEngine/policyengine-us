"""Every county FIPS dataset row must map to a County enum member.

The county FIPS dataset is the bridge from ``county_fips`` inputs to the
``County`` enum; a row present in the dataset but absent from the enum
degrades to UNKNOWN for every household carrying that FIPS code (and,
before ``map_county_string_to_enum`` tolerated misses, raised a KeyError
over microsimulation datasets).
"""

import numpy as np

from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    map_county_string_to_enum,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)

UNKNOWN_INDEX = County._member_names_.index("UNKNOWN")


def test_every_county_fips_row_maps_to_an_enum_member():
    dataset = load_county_fips_dataset()

    mapped = map_county_string_to_enum(
        dataset["county_name"],
        dataset["state"],
    )

    unmapped = dataset.loc[
        np.asarray(mapped) == UNKNOWN_INDEX, ["county_name", "state"]
    ]
    assert unmapped.empty, (
        f"{len(unmapped)} county FIPS dataset row(s) have no County enum "
        f"member: {unmapped.head(10).to_dict('records')}"
    )


def test_unmapped_names_return_unknown_without_raising():
    import pandas as pd

    mapped = map_county_string_to_enum(
        pd.Series(["No Such County"]),
        pd.Series(["ZZ"]),
    )

    assert np.asarray(mapped).tolist() == [UNKNOWN_INDEX]
