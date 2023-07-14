from policyengine_us.model_api import *


class va_map_pregnant_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP Pregnant Women income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        earned = person("va_map_earned_income", period) 
        unearned = person("va_map_unearned_income", period)
        child = person("is_child")
        mother = person("is_mother")
        father = person("is_father")
        c = child | mother | father
        income = spm_unit.sum(earned + unearned) * c
        
        limit = spm_unit("va_map_pregnant_income_limit", period)
        return income <= limit
