from policyengine_us.model_api import *


class pell_grant_uses_sai(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Pell Grant uses the Student Aid Index"

    def formula(person, period, parameters):
        return True

    def formula_2024(person, period, parameters):
        return True

    def formula_2023(person, period, parameters):
        return False
