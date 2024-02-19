from policyengine_us.model_api import *


class heating_cooling_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Heating and cooling expense"
    unit = USD
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        heating_expense = person("heating_expense", period)
        cooling_expense = person("cooling_expense", period)
        return spm_unit.sum(heating_expense + cooling_expense)
