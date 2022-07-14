from openfisca_us.model_api import *
from openfisca_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


class county(Variable):
    value_type = Enum
    possible_values = County
    default_value = County.UNKNOWN
    entity = Household
    label = "County"
    definition_period = ETERNITY

    def formula(household, period, parameters):
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
        return np.array(
            [
                getattr(County, f"{county_key}_{state}")
                if hasattr(County, f"{county_key}_{state}")
                else County.UNKNOWN
                for county_key, state in zip(county_key, state_code)
            ]
        )
