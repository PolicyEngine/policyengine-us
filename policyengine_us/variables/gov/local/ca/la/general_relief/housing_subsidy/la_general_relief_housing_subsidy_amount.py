from policyengine_us.model_api import *


class la_general_relief_housing_subsidy_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Los Angeles County General Relief county housing subsidy amount"
    definition_period = MONTH
    defined_for = "la_general_relief_housing_subsidy_eligible"
    reference = (
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/gr/homelessness/housing-subsidy-management-program.html#custom-title-f75ca3f760",
        "https://dpss.lacounty.gov/content/dam/dpss/documents/en/gr/gr-housing-subsidy/PA%206182%20%28English%29%20ADA%20APPROVED.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(period).gov.local.ca.la.general_relief.housing_subsidy
        subsidy_amount = where(married, p.amount.married, p.amount.single)
        rent = add(spm_unit, period, ["rent"])
        # County assistance excludes the participant's GR contribution.
        # Capping at rent makes the subsidy zero when there is no rent.
        return min_(rent, subsidy_amount)
