from policyengine_us.model_api import *


class ma_eaedc_standard_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC standard assistance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/lists/emergency-aid-to-the-elderly-disabled-and-children-eaedc-grant-calculation"

    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period)
        living_arrangement = spm_unit("ma_eaedc_living_arrangement", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.standard_assistance.amount
        p1 = p.base[living_arrangement]
        pn = p.additional[living_arrangement]
        return p1 + pn * (n - 1)
