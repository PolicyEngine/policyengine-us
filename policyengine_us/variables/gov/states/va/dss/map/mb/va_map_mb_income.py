from policyengine_us.model_api import *


class va_map_mb_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP MB countable income"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        married = add(spm_unit, period, ["is_married"]) > 0
        earned = person("va_map_earned_income", period)
        unearned = person("va_map_unearned_income", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        income = earned + unearned

        return spm_unit.sum(income * where(married, head | spouse, head))
