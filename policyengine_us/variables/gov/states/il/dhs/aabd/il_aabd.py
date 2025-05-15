from policyengine_us.model_api import *


class il_aabd(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) cash benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        total_needs = person("il_aabd_need_standard_person", period)
        countable_income = person("il_aabd_countable_income", period)
        aabd_amount = max_(total_needs - countable_income, 0)

        return spm_unit.sum(aabd_amount)
