from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    second_lowest_silver_plan_cost,
)
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    aca_rating_areas,
)


class slspc_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        simulation: Simulation = household.simulation

        # Check for existing SLSPC first
        if (
            simulation.get_holder("reported_slspc").get_array(period)
            is not None
        ):
            return "reported_slspc"

        # Get county data
        county = household("county_str", period)

        # Create DataFrame with county information
        df = pd.DataFrame(
            {
                "location": county,
            }
        )

        # Single merge with medicaid_rating_areas
        df_matched = pd.merge(
            df,
            aca_rating_areas,
            how="left",
            left_on="location",
            right_on="location",
        )

        # Fill any missing values with default rating area 1
        return df_matched["rating_area"].fillna(1)
