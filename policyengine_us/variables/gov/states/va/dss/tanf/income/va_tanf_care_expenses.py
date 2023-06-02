from policyengine_us.model_api import *


class va_tanf_care_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF care expenses"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    
    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        child_0_17 = person("is_child", period)
        adult = person("is_adult", period)
        disabled = person("is_disabled", period)
        disabled_adult = adult & disabled
        number = spm_unit.sum(child_0_17 | disabled_adult)

        return 