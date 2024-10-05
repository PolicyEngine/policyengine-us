from policyengine_us.model_api import *


class la_general_relief_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Los Angeles County General Relief Housing Subsidy"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_housing_subsidy_eligible"
    reference = "https://dpss.lacounty.gov/en/cash/gr/housing.html"

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(period).gov.local.ca.la.general_relief.housing_subsidy
        subsidy_amount = where(married, p.amount.married, p.amount.single)
        # If filers are receiving the housing subsidy, they are obligated
        # to contribute an amount of their GR towards rent
        rent_contributions = spm_unit(
            "la_general_relief_rent_contribution", period
        )
        # The amount can not exceed rent
        rent = add(spm_unit, period, ["rent"])
        return min_(rent, subsidy_amount + rent_contributions)
