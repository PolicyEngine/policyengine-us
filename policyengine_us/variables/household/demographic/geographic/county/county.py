from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    map_county_string_to_enum,
)


def latest_readable_county(simulation: Simulation):
    """The latest county this simulation was given and can read, if any.

    Only inputs count. A county this simulation calculated belongs to its year:
    read for a later year, it would keep a household in its old county after
    ``state_fips`` moves it, and only when the earlier year ran first.

    The holder lists the periods of every array in its storage, whichever
    branch stored them. A branch reused for a later year holds its own values
    for earlier years, which only a read with its branch name finds, so ask for
    the input periods this branch reads and read with its name.
    """
    holder = simulation.get_holder("county")
    input_periods = holder.get_input_periods(simulation.branch_name)
    if not input_periods:
        return None
    latest_period = max(
        input_periods,
        key=lambda period: (period.start, period.stop, str(period)),
    )
    return holder.get_array(latest_period, simulation.branch_name)


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
        if simulation.is_over_dataset:
            stored_county = latest_readable_county(simulation)
            if stored_county is not None:
                return stored_county
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
