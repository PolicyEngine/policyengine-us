from policyengine_us.model_api import *


class ca_fytc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Foster Youth Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth

        eligible_people = add(tax_unit, period ["ca_eitc_eligible"])

        head_earned_income = tax_unit("head_earned", period)

        spouse_earned_income = tax_unit("spouse_earned", period)
        
        head_and_spouse_earned = head_earned_income + spouse_earned_income

        reduction_amount = max_(0, (head_and_spouse_earned - p.threshold) * p.reduction)

        return min_(p.max_amount, head_and_spouse_earned - reduction_amount) * eligible_people 
