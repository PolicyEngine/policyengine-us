from policyengine_us.model_api import *


class has_heating_cooling_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has heating/cooling costs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        heating_expense = person("heating_expense", period)
        cooling_expense = person("cooling_expense", period)
        return spm_unit.sum(heating_expense + cooling_expense) > 0
        # return add(spm_unit, period, ["heating_cooling_expense"]) > 0
