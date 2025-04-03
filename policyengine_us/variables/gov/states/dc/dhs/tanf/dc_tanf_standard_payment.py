from policyengine_us.model_api import *


class dc_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "DC Temporary Assistance for Needy Families (TANF) standard payment"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.dc.dhs.tanf
        return p.standard_payment[unit_size]
