from policyengine_us.model_api import *


class la_general_relief_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Los Angeles County General Relief Housing Subsidy"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_housing_subsidy_eligible"
    reference = (
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/gr/homelessness/housing-subsidy-management-program.html#custom-title-f75ca3f760",
        "https://dpss.lacounty.gov/content/dam/dpss/documents/en/gr/gr-housing-subsidy/PA%206182%20%28English%29%20ADA%20APPROVED.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(period).gov.local.ca.la.general_relief.housing_subsidy
        subsidy_amount = where(married, p.amount.married, p.amount.single)
        # DPSS 46-103 specifies the landlord payment as subsidy plus the
        # scheduled GR contribution. Read the schedule independently of the
        # grant deduction, which depends on receiving this housing payment.
        rent_contributions = where(
            married, p.rent_contribution.married, p.rent_contribution.single
        )
        # The amount can not exceed rent
        rent = add(spm_unit, period, ["rent"])
        return min_(rent, subsidy_amount + rent_contributions)
