from policyengine_us.model_api import *


class amt_kiddie_tax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax kiddie tax applies"
    documentation = "Whether the kiddie tax applies to the tax unit"

    def formula(tax_unit, period, parameters):
        age_head = tax_unit("age_head", period)
        p = parameters(period).gov.irs.dependent.ineligible_age
        young_head = (age_head != 0) & (age_head < p.non_student)
        no_or_young_spouse = tax_unit("age_spouse", period) < p.non_student
        return young_head & no_or_young_spouse
