from policyengine_us.model_api import *


class id_grocery_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Idaho grocery credit"
    definition_period = YEAR
    defined_for = "StateCode.ID"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.gc
        head_aged = tax_unit("age_head", period) >= p.age_eligibility
        spouse_aged = tax_unit("age_spouse ", period) >= p.age_eligibility

        p = parameters(period).gov.states.id.tax.income.credits.gc

        return head_aged | spouse_aged
