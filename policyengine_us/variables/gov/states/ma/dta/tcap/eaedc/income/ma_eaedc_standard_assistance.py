from policyengine_us.model_api import *


class ma_eaedc_standard_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC standard_assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-440"
    )

    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period)
        living_arrangement = spm_unit("ma_eaedc_living_arrangement", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.standard_assistance.amount
        p1 = p.base[living_arrangement] * MONTHS_IN_YEAR
        pn = p.additional[living_arrangement] * MONTHS_IN_YEAR
        return p1 + pn * (n - 1)
