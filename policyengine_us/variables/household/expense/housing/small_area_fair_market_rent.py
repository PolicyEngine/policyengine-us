from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.fmr import (
    small_area_fair_market_rents,
    nearest_safmr_year,
)

# HUD publishes Small Area FMRs for 0-4 bedrooms; larger units add 15% of the
# 4-bedroom value per additional bedroom, matching `hud_fair_market_rent`.
EXTRA_BEDROOM_SAFMR_INCREMENT = 0.15


class small_area_fair_market_rent(Variable):
    value_type = float
    entity = Household
    label = "Small area fair market rent"
    unit = USD
    definition_period = YEAR
    reference = "https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html"

    def formula(household, period, parameters):
        zip_code = household("zip_code", period)
        bedrooms = household("bedrooms", period)
        lookup_bedrooms = np.clip(bedrooms.astype(int), 0, 4)
        extra_bedrooms = max_(bedrooms - 4, 0)
        year = nearest_safmr_year(period.start.year)
        df = pd.DataFrame(
            {
                "zip_code": np.asarray(zip_code).astype(str),
                "bedrooms": lookup_bedrooms,
                "year": year,
            }
        )
        df["zip_code"] = df["zip_code"].str.zfill(5)
        matched = df.merge(
            small_area_fair_market_rents[
                ["zip_code", "bedrooms", "year", "value"]
            ].astype({"zip_code": str, "bedrooms": int}),
            on=["zip_code", "bedrooms", "year"],
            how="left",
            validate="many_to_one",
        )
        monthly_safmr = matched["value"].fillna(0).to_numpy()
        bedroom_adjustment = 1 + EXTRA_BEDROOM_SAFMR_INCREMENT * extra_bedrooms
        return monthly_safmr * bedroom_adjustment * MONTHS_IN_YEAR
