from policyengine_us.model_api import *


class head_of_household_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for head of household filing status"
    reference = "https://www.law.cornell.edu/uscode/text/26/2#b"

    def formula(tax_unit, period, parameters):
        married = tax_unit("tax_unit_married", period)
        # is_child_dependent includes qualifying children, qualifying
        # relatives, and permanently disabled individuals
        has_qualifying_person = (
            tax_unit("tax_unit_child_dependents", period) > 0
        )
        return (
            has_qualifying_person
            & ~married
            & ~tax_unit("surviving_spouse_eligible", period)
        )
