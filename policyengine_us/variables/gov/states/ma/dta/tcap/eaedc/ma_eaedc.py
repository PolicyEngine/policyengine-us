from policyengine_us.model_api import *


class ma_eaedc(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC"
    unit = USD
    definition_period = MONTH
    defined_for = "ma_eaedc_if_tafdc_ineligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-701.000"

    # Program value can not be less than 0
    # due to the eligibility requirements
    def formula(spm_unit, period, parameters):
        tafdc_exceeds_eaedc = spm_unit("ma_tafdc_larger_than_eaedc", period)
        standard_assistance = spm_unit("ma_eaedc_standard_assistance", period)
        net_income = spm_unit("ma_eaedc_net_income", period)
        return ~tafdc_exceeds_eaedc * (standard_assistance - net_income)
