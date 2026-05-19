from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation
from policyengine_us.tools.geography.county_helpers import (
    map_county_string_to_enum,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
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

        # When running over a dataset, use stored county data if available
        # (geographic variables like county are time-invariant for households)
        if simulation.is_over_dataset:  # pragma: no cover
            # Microsimulation-specific path - tested via microsim
            holder = simulation.get_holder("county")
            known_periods = holder.get_known_periods()
            if len(known_periods) > 0:
                last_known_period = sorted(known_periods)[-1]
                return holder.get_array(last_known_period)
            return household("first_county_in_state", period)

        # First look if county FIPS is provided; if so, map to county name
        county_fips: "pd.Series[str]" | None = household("county_fips", period)

        COUNTY_FIPS_DATASET: "pd.DataFrame" = load_county_fips_dataset()

        # Decode FIPS codes
        county_fips_codes = COUNTY_FIPS_DATASET.set_index("county_fips")
        result = household("first_county_in_state", period)
        county_fips = np.asarray(county_fips).astype(str)
        known_fips = county_fips != ""
        valid_fips = known_fips & np.isin(county_fips, county_fips_codes.index)
        if valid_fips.any():
            county_name = county_fips_codes.loc[
                county_fips[valid_fips],
                "county_name",
            ]
            state_code = county_fips_codes.loc[county_fips[valid_fips], "state"]
            result = np.array(result, copy=True)
            result[valid_fips] = map_county_string_to_enum(
                county_name,
                state_code,
            ).to_numpy()
        return result
