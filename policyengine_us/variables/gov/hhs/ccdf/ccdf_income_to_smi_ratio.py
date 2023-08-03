from policyengine_us.model_api import *


class ccdf_income_to_smi_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income to SMI ratio"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("ccdf_income", period)
        smi = spm_unit("hhs_smi", period)
        return income / smi
