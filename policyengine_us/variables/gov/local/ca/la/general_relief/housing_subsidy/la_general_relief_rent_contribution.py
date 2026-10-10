from policyengine_us.model_api import *


class la_general_relief_rent_contribution(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Los Angeles County General Relief rent contribution"
    definition_period = MONTH
    defined_for = "la_general_relief_eligible"
    reference = (
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/gr/homelessness/housing-subsidy-management-program.html#custom-title-f75ca3f760",
        "https://dpss.lacounty.gov/content/dam/dpss/documents/en/gr/gr-housing-subsidy/PA%206182%20%28English%29%20ADA%20APPROVED.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(period).gov.local.ca.la.general_relief
        # PA 6182 deducts the participant's contribution from cash GR.
        # Read the county subsidy rather than the total landlord payment,
        # which includes this contribution.
        receive_housing_subsidy = (
            spm_unit("la_general_relief_housing_subsidy_amount", period) > 0
        )
        rent_contributions = where(
            married,
            p.housing_subsidy.rent_contribution.married,
            p.housing_subsidy.rent_contribution.single,
        )

        return where(receive_housing_subsidy, rent_contributions, 0)
