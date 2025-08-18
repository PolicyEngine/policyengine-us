from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation
from policyengine_us.tools.geography.county_helpers import (
    map_county_string_to_enum,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us.data import ZIP_CODE_DATASET
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
        simulation: Simulation = household.simulation

        # First look if county FIPS is provided; if so, map to county name
        county_fips: "pd.Series[str]" | None = household("county_fips", period)

        if not simulation.is_over_dataset and county_fips.all():
            COUNTY_FIPS_DATASET: "pd.DataFrame" = load_county_fips_dataset()

            # Decode FIPS codes
            county_fips_codes = COUNTY_FIPS_DATASET.set_index("county_fips")
            county_name = county_fips_codes.loc[county_fips, "county_name"]
            state_code = county_fips_codes.loc[county_fips, "state"]
            return map_county_string_to_enum(county_name, state_code)

        # Check if zip_code was explicitly provided as input
        # The zip_code variable auto-generates values, so we need to check if it was user input
        input_variables = getattr(simulation, "input_dataset", {})
        if (
            isinstance(input_variables, dict)
            and "zip_code" not in input_variables
        ):
            # No ZIP code was provided by user, use first county in state
            return household("first_county_in_state", period)

        # Attempt to look up from ZIP code (only if explicitly provided)
        try:
            zip_code = household("zip_code", period).astype(int)
            zip_codes = ZIP_CODE_DATASET.set_index("zip_code")
            county_name = zip_codes.county[zip_code]
            state_code = zip_codes.state[zip_code]
            return map_county_string_to_enum(county_name, state_code)
        except:
            # If ZIP code lookup fails, use first county in state as fallback
            return household("first_county_in_state", period)
