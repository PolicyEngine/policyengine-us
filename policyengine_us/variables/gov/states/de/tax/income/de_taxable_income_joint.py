from policyengine_us.model_api import *


class de_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware taxable income when married filing jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        agi = person("de_agi", period)
        is_head = person("is_tax_unit_head", period)
        total_agi = is_head * person.tax_unit.sum(agi)
        deductions = person("de_deduction_joint", period)
        total_deductions = person.tax_unit.sum(deductions)
        return max_(total_agi - total_deductions, 0)
