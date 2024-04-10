from policyengine_us.model_api import *


class de_taxable_income_indv(Variable):
    value_type = float
    entity = Person
    label = (
        "Delaware taxable income when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        agi = person("de_agi_indiv", period)
        deductions = person("de_deduction_indv", period)
        return max_(0, agi - deductions)
