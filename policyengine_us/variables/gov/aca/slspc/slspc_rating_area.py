from policyengine_us.model_api import *

from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    aca_rating_areas,
)


class slspc_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        # Get county data
        county = household("county_str", period)

        # Create DataFrame with county information
        df = pd.DataFrame({"county": county})

        # Single merge with medicaid_rating_areas
        df_matched = pd.merge(
            df,
            aca_rating_areas,
            how="left",
            left_on="county",
            right_on="county",
        )

        # Fill any missing values with default rating area 1
        return df_matched["rating_area"].fillna(1)
