from policyengine_us.model_api import *


class de_aged_additional_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged additional standard deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.deductions

        age_head = tax_unit("age_head", period)
        head_eligible = (age_head >= 65).astype(int)

        age_spouse = tax_unit("age_spouse", period)
        spouse_eligible = (age_spouse >= 65).astype(int)

        return (head_eligible + spouse_eligible) * p.yourself_aged
