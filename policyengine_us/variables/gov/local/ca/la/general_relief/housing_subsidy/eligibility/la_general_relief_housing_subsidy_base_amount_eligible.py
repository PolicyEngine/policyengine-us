from policyengine_us.model_api import *


class la_general_relief_housing_subsidy_base_amount_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief Housing Subsidy based on the base amount requirements"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_eligible"
    reference = "https://dpss.lacounty.gov/en/cash/gr/housing.html"

    def formula(spm_unit, period, parameters):
        # General relief cannot be under the rent subsidy amounts
        gr_base_amount = spm_unit("la_general_relief_base_amount", period)
        p = parameters(
            period
        ).gov.local.ca.la.general_relief.housing_subsidy.rent_contribution
        married = add(spm_unit, period, ["is_married"])
        rent_contribution = where(married, p.married, p.single)
        return gr_base_amount >= rent_contribution
