from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.payment_standards import (
    zip_code_payment_standards,
    nearest_payment_standard_year,
)

# Published schedules cover 0-6 bedrooms; larger units add 15% of the
# 6-bedroom value per additional bedroom.
EXTRA_BEDROOM_INCREMENT = 0.15


class zip_code_payment_standard(Variable):
    value_type = float
    entity = Household
    label = "ZIP code-level HUD payment standard"
    unit = USD
    documentation = (
        "PHA-published Housing Choice Voucher payment standard for the "
        "household's ZIP code, where one is encoded. Zero otherwise."
    )
    definition_period = YEAR
    reference = "https://www.tdhca.texas.gov/section-8-housing-choice-voucher-program"

    def formula(household, period, parameters):
        zip_code = household("zip_code", period)
        bedrooms = household("bedrooms", period)
        lookup_bedrooms = np.clip(bedrooms.astype(int), 0, 6)
        extra_bedrooms = max_(bedrooms - 6, 0)
        year = nearest_payment_standard_year(period.start.year)
        df = pd.DataFrame(
            {
                "zip_code": np.asarray(zip_code).astype(str),
                "bedrooms": lookup_bedrooms,
                "year": year,
            }
        )
        df["zip_code"] = df["zip_code"].str.zfill(5)
        matched = df.merge(
            zip_code_payment_standards[
                ["zip_code", "bedrooms", "year", "value"]
            ].astype({"zip_code": str, "bedrooms": int}),
            on=["zip_code", "bedrooms", "year"],
            how="left",
        )
        monthly_standard = matched["value"].fillna(0).to_numpy()
        bedroom_adjustment = 1 + EXTRA_BEDROOM_INCREMENT * extra_bedrooms
        return monthly_standard * bedroom_adjustment * MONTHS_IN_YEAR
