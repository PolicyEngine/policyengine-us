from policyengine_us.model_api import *


class tanf_amount_if_eligible(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "TANF amount if family is eligible"
    documentation = "How much a family would receive if they were eligible for Temporary Assistance for Needy Families benefit."
    unit = USD

    def formula(spm_unit, period, parameters):
        max_amount = spm_unit("tanf_max_amount", period)
        countable_income = spm_unit("tanf_countable_income", period)
        return max_(0, max_amount - countable_income)
