from policyengine_us.model_api import *


class is_ccdf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Income eligibility for CCDF"

    def formula(spm_unit, period, parameters):
        income_to_smi_ratio = spm_unit("ccdf_income_to_smi_ratio", period)
        p_ratio_limit = parameters(period).gov.hhs.ccdf.income_limit_smi
        return income_to_smi_ratio <= p_ratio_limit
