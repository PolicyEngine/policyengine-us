from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    map_county_string_to_enum,
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
            # No stored county: fall through to the county_fips mapping, so
            # datasets that store county_fips compute counties from it
            # instead of collapsing to first_county_in_state.

        # First look if county FIPS is provided; if so, map to county name
        county_fips: "pd.Series[str]" | None = household("county_fips", period)

        county_fips = np.asarray(county_fips).astype(str)
        known_fips = county_fips != ""
        if not known_fips.any():
            return household("first_county_in_state", period)

        COUNTY_FIPS_DATASET: "pd.DataFrame" = load_county_fips_dataset()
        counties = pd.merge(
            pd.DataFrame({"county_fips": county_fips[known_fips]}),
            COUNTY_FIPS_DATASET,
            on="county_fips",
            how="left",
        )
        valid_fips = counties["county_name"].notna().to_numpy()
        if known_fips.all() and valid_fips.all():
            return map_county_string_to_enum(
                counties["county_name"],
                counties["state"],
            ).to_numpy()

        result = household("first_county_in_state", period)
        if not valid_fips.any():
            return result

        known_indices = np.where(known_fips)[0]
        result = np.array(result, copy=True)
        county_name = counties.loc[valid_fips, "county_name"]
        state_code = counties.loc[valid_fips, "state"]
        result[known_indices[valid_fips]] = map_county_string_to_enum(
            county_name,
            state_code,
        ).to_numpy()
        return result
