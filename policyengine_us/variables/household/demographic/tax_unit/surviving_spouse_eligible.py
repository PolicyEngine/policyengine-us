from policyengine_us.model_api import *


class surviving_spouse_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for surviving spouse filing status"
    reference = "https://www.law.cornell.edu/uscode/text/26/2#a"

    def formula(tax_unit, period, parameters):
        # The surviving spouse filing status should only apply to surviving spouse heads
        # who maintain a household for at least one dependent
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_surviving_spouse = person("is_surviving_spouse", period)
        surviving_spouse_head = tax_unit.any(is_head & is_surviving_spouse)
        has_child_dependents = (
            tax_unit("tax_unit_child_dependents", period) > 0
        )
        married = tax_unit("tax_unit_married", period)
        return surviving_spouse_head & has_child_dependents & ~married
