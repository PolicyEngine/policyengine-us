from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.fmr import (
    available_fmr_years,
    fair_market_rents,
    nearest_fmr_year,
)


EXTRA_BEDROOM_FMR_INCREMENT = 0.15
FMR_LOOKUP = fair_market_rents.astype({"county_fips": str, "bedrooms": int})


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
        lookup_bedrooms = np.clip(bedrooms.astype(int), 0, 4)
        extra_bedrooms = max_(bedrooms - 4, 0)
        year = nearest_fmr_year(period.start.year)
        df = pd.DataFrame(
            {
                "row_id": np.arange(len(county_fips)),
                "county_fips": county_fips,
                "bedrooms": lookup_bedrooms,
                "year": year,
            }
        )
        df["county_fips"] = df["county_fips"].astype(str).str.zfill(5)
        matched = df.merge(
            FMR_LOOKUP,
            on=["county_fips", "bedrooms", "year"],
            how="left",
        )
        monthly_fmr = matched["value"].copy()
        for fallback_year in sorted(
            [candidate for candidate in available_fmr_years if candidate < year],
            reverse=True,
        ):
            missing = monthly_fmr.isna()
            if not missing.any():
                break
            fallback = df.loc[missing, ["row_id", "county_fips", "bedrooms"]].assign(
                year=fallback_year
            )
            fallback_matched = fallback.merge(
                FMR_LOOKUP,
                on=["county_fips", "bedrooms", "year"],
                how="left",
            ).dropna(subset=["value"])
            monthly_fmr.iloc[fallback_matched["row_id"].to_numpy()] = fallback_matched[
                "value"
            ].to_numpy()
        monthly_fmr = monthly_fmr.fillna(0).to_numpy()
        bedroom_adjustment = 1 + EXTRA_BEDROOM_FMR_INCREMENT * extra_bedrooms
        return monthly_fmr * bedroom_adjustment * MONTHS_IN_YEAR
