from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    aca_rating_areas,
)


class slcsp_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        county = household("county_str", period)
        is_la = county == "LOS_ANGELES_COUNTY_CA"

        if is_la:
            zip3 = household("three_digit_zip_code", period)
            p = parameters(period).gov.aca
            return p.la_county_rating_area[zip3]
        # If not LA, merge with aca_rating_areas.
        df = pd.DataFrame({"county": county})
        aca_rating_areas["rating_area"] = aca_rating_areas[
            "rating_area"
        ].astype(str)
        df_matched = pd.merge(
            df,
            aca_rating_areas,
            how="left",
            left_on="county",
            right_on="county",
        )
        return df_matched["rating_area"].fillna(1)
