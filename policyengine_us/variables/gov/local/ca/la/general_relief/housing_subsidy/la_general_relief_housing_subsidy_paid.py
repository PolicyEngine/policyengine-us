from policyengine_us.model_api import *


class la_general_relief_housing_subsidy_paid(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Los Angeles County General Relief county housing subsidy paid"
    definition_period = MONTH
    reference = (
        "https://dpss.lacounty.gov/content/dam/dpss/documents/en/gr/gr-housing-subsidy/PA%206182%20%28English%29%20ADA%20APPROVED.pdf#page=1",
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/gr/homelessness/housing-subsidy-management-program.html#custom-title-f75ca3f760",
    )

    def formula(spm_unit, period, parameters):
        housing_payment = spm_unit("la_general_relief_housing_subsidy", period)
        rent_contribution = spm_unit("la_general_relief_rent_contribution", period)
        # PA 6182, page 1, items 2-3: the landlord receives the direct-rent
        # contribution and additional county subsidy as separate components.
        # With $500 rent: min(500, 475 + 100) - 100 = $400 county aid.
        # Retain the fixed contribution when rent is lower, with no negative aid.
        # Read actual payment without another mask so supplied inputs apply.
        return max_(housing_payment - rent_contribution, 0)
