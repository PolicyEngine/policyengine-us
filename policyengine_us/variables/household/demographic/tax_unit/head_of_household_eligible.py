from policyengine_us.model_api import *


class head_of_household_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for head of household filing status"
    reference = "https://www.law.cornell.edu/uscode/text/26/2#b"

    def formula(tax_unit, period, parameters):
        married = tax_unit("tax_unit_married", period)
        has_child_dependents = (
            tax_unit("tax_unit_child_dependents", period) > 0
        )
        return (
            has_child_dependents
            & ~married
            & ~tax_unit("surviving_spouse_eligible", period)
        )
