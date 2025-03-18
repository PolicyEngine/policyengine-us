from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us_data import ZIP_CODE_DATASET, COUNTY_FIPS_DATASET


class county(Variable):
    value_type = Enum
    possible_values = County
    default_value = County.UNKNOWN
    entity = Household
    label = "County"
    definition_period = YEAR

    def formula(household, period, parameters):
        # First look if county FIPS is provided; if so, map to county name
        county_fips: int | None = household("county_fips", period)
        if county_fips.all():
            # Find county name from dataset
            county_fips_codes = COUNTY_FIPS_DATASET.set_index("county_fips")
            county_name = county_fips_codes.loc[county_fips, "county_name"]
            state_code = county_fips_codes.loc[county_fips, "state"]
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

        # Attempt to look up from ZIP code
        zip_code = household("zip_code", period).astype(int)
        zip_codes = ZIP_CODE_DATASET.set_index("zip_code")
        county_name = zip_codes.county[zip_code]
        state_code = zip_codes.state[zip_code]
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
            np.arange(len(County._member_names_)), index=County._member_names_
        )
        return county_names[county_state]
