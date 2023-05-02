from policyengine_us.model_api import *


class dc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "dc_tanf_eligible"

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("dc_tanf_grant_standard", period)
        countable_income = spm_unit("dc_tanf_countable_income", period)
        return max_(grant_standard - countable_income, 0)
