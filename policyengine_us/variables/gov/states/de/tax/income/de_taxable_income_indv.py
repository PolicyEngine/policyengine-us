from policyengine_us.model_api import *


class de_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = (
        "Delaware taxable income when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    defined_for = "de_can_file_separate_on_same_return"

    def formula(person, period, parameters):
        agi = person("de_agi", period)
        deductions = person("de_deduction_indiv", period)
        return max_(0, agi - deductions)
