from policyengine_us.model_api import *


class ma_eaedc_financially_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Financially eligible for the Massachusetts EAEDC "
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B)

    def formula(spm_unit, period, parameters):
        standard_assistance = spm_unit("ma_eaedc_standard_assistance", period)
        net_income = spm_unit("ma_eaedc_net_income", period)
        return net_income <= standard_assistance
