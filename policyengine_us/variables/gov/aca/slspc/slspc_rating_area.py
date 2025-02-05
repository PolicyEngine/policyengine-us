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
        is_la = county == "Los Angeles County, CA"

        if is_la:
            zip3 = household("three_digit_zip_code", period)
            la_data = parameters.gov.aca.la_county_rating_area[period]
            # Indent this block to be part of the if statement
            for rating_area, zip_codes in la_data.items():
                if zip3 in zip_codes:
                    return rating_area

        # Create DataFrame with county information
        df = pd.DataFrame({"county": county})

        # Turn rating_area into an int.
        aca_rating_areas["rating_area"] = aca_rating_areas["rating_area"].astype(str)

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
