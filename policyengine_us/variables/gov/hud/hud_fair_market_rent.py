from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.fmr import fair_market_rents


class hud_fair_market_rent(Variable):
    value_type = float
    entity = Household
    label = "HUD Fair Market Rent"
    unit = USD
    definition_period = YEAR
    reference = "https://www.huduser.gov/portal/datasets/fmr.html"

    def formula(household, period, parameters):
        county_fips = household("county_fips", period)
        bedrooms = household("bedrooms", period)
        year = period.start.year
        df = pd.DataFrame(
            {
                "county_fips": county_fips,
                "bedrooms": bedrooms.astype(int),
                "year": year,
            }
        )
        df["county_fips"] = df["county_fips"].astype(str).str.zfill(5)
        matched = df.merge(
            fair_market_rents.astype({"county_fips": str, "bedrooms": int}),
            on=["county_fips", "bedrooms", "year"],
            how="left",
        )
        return matched["value"].fillna(0).to_numpy() * MONTHS_IN_YEAR
