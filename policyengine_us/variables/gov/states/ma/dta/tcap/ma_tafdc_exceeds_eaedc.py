from policyengine_us.model_api import *


class ma_tafdc_exceeds_eaedc(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether the TAFDC value exceeds the EAEDC value"
    definition_period = MONTH
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        tafdc_value = spm_unit("ma_tafdc_if_claimed", period)
        eaedc_value = spm_unit("ma_eaedc_if_claimed", period)
        return tafdc_value > eaedc_value
