from policyengine_us.model_api import *
from policyengine_us.tools.geography.county_helpers import (
    map_county_string_to_enum,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us_data import ZIP_CODE_DATASET
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
)


class county(Variable):
    value_type = Enum
    possible_values = County
    default_value = County.UNKNOWN
    entity = Household
    label = "County"
    definition_period = YEAR

    def formula(household, period, parameters):

        # First look if county FIPS is provided; if so, map to county name
        county_fips: "pd.Series[str]" | None = household("county_fips", period)

        if county_fips.all():
            COUNTY_FIPS_DATASET: "pd.DataFrame" = load_county_fips_dataset()

            # Decode FIPS codes
            county_fips_codes = COUNTY_FIPS_DATASET.set_index("county_fips")
            county_name = county_fips_codes.loc[county_fips, "county_name"]
            state_code = county_fips_codes.loc[county_fips, "state"]
            return map_county_string_to_enum(county_name, state_code)

        # Attempt to look up from ZIP code
        zip_code = household("zip_code", period).astype(int)
        zip_codes = ZIP_CODE_DATASET.set_index("zip_code")
        county_name = zip_codes.county[zip_code]
        state_code = zip_codes.state[zip_code]
        return map_county_string_to_enum(county_name, state_code)
