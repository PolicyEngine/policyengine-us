from policyengine_us.model_api import *


class ma_eaedc_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts EAEDC based on income"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-285"
    )

    def formula(spm_unit, period, parameters):
        standard_assistance = spm_unit("ma_eaedc_standard_assistance", period)
        # Income after deductions as applied in the net income test
        net_income = spm_unit("ma_eaedc_net_income", period)
        return net_income <= standard_assistance
