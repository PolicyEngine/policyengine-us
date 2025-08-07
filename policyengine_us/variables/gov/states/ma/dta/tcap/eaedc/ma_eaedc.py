from policyengine_us.model_api import *


class ma_eaedc(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC"
    unit = USD
    definition_period = MONTH
    defined_for = "ma_eaedc_eligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-701.000"

    def formula(spm_unit, period, parameters):
        tafdc_exceeds_eaedc = spm_unit("ma_tafdc_exceeds_eaedc", period)
        eaedc_benefit_amount = spm_unit("ma_eaedc_if_claimed", period)
        return ~tafdc_exceeds_eaedc * eaedc_benefit_amount
