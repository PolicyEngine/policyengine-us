from policyengine_us.model_api import *


class mn_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_assets", period)
