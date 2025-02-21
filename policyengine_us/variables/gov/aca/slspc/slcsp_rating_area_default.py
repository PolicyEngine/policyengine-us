from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    aca_rating_areas,
)


class slcsp_rating_area_default(Variable):
    value_type = int
    entity = Household
    label = (
        "Second-lowest ACA silver-plan cost rating area outside of LA County"
    )
    definition_period = YEAR

    def formula(household, period, parameters):
        # 1) Read the county string from the Household
        county_str = household("county_str", period)

        # 2) Ensure 'rating_area' is a string in aca_rating_areas
        aca_rating_areas["rating_area"] = aca_rating_areas[
            "rating_area"
        ].astype(str)

        # 3) Create a DataFrame using county_str
        df = pd.DataFrame({"county": county_str})

        # 4) Merge on "county"
        df_matched = pd.merge(
            df,
            aca_rating_areas,
            how="left",
            on="county",
        )

        # 5) Fill missing rating areas with "1", convert to int
        df_matched["rating_area"] = (
            df_matched["rating_area"].fillna("1").astype(int)
        )

        # 6) Return the rating_area column
        return df_matched["rating_area"]
