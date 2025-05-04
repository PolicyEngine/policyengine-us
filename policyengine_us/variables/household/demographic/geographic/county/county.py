'''
from policyengine_us.model_api import *
from policyengine_us.tools.geography.county_helpers import (
    map_county_string_to_enum,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us_data import ZIP_CODE_DATASET
import pandas as pd  # Added import for pandas


class County(Variable):
    value_type = Enum
    possible_values = County
    default_value = County.UNKNOWN
    entity = Household
    label = "County"
    definition_period = YEAR

    def formula(household, period, parameters):

        # First look if county FIPS is provided; if so, map to county name
        county_fips: "pd.Series[str]" | None = household("county_fips", period)

        # Check if the series is not None and contains non-empty strings
        # Using .any() would be better if we want to proceed if at least one is provided
        # but the original logic used .all(), so keeping that for consistency.
        if county_fips is not None and county_fips.notna().all() and (county_fips != '').all():
            COUNTY_FIPS_DATASET: "pd.DataFrame" = load_county_fips_dataset()

            # Prepare input DataFrame
            input_df = pd.DataFrame({'county_fips': county_fips})

            # Perform left merge
            merged_df = pd.merge(input_df, COUNTY_FIPS_DATASET, on='county_fips', how='left')

            # Extract results
            county_name = merged_df['county_name']
            state_code = merged_df['state']
            # Handle potential misses from the merge (NaNs)
            county_name = county_name.fillna("Unknown")
            state_code = state_code.fillna("Unknown")

            return map_county_string_to_enum(county_name, state_code)

        # Attempt to look up from ZIP code if FIPS lookup didn't proceed
        zip_code = household("zip_code", period)
        # Ensure zip_code is int, handle potential NaNs or non-numeric before astype
        zip_code_clean = pd.to_numeric(zip_code, errors='coerce').fillna(0).astype(int)
        
        zip_codes = ZIP_CODE_DATASET.set_index("zip_code")
        
        # Use reindex to handle missing zip codes gracefully, fill with unknowns
        county_name = zip_codes.reindex(zip_code_clean)["county"].fillna("Unknown")
        state_code = zip_codes.reindex(zip_code_clean)["state"].fillna("Unknown")
        
        return map_county_string_to_enum(county_name, state_code)
'''