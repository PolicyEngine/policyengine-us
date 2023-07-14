from policyengine_us.model_api import *


class va_map_mb_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP MB QI countable income"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        earned = person("va_map_earned_income", period) 
        unearned = person("va_map_unearned_income", period)
        mother = person("is_mother")
        father = person("is_father")
        c = mother | father
        
        return spm_unit.sum(earned + unearned) * c
