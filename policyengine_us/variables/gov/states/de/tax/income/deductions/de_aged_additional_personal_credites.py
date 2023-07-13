from policyengine_us.model_api import *


class de_aged_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged additional personal credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.deductions

        age_head = tax_unit("age_head", period)
        head_eligible = p.age_eligibility.calc(age_head)

        age_spouse = tax_unit("age_spouse", period)
        spouse_eligible = p.age_eligibility.calc(age_spouse)

        return head_eligible + spouse_eligible
