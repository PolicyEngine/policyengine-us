from policyengine_us.model_api import *


class la_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.exemptions
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_amount = p.aged.calc(age_head)
        spouse_amount = p.aged.calc(age_spouse)
        return head_amount + spouse_amount
