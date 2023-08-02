from policyengine_us.model_api import *


class dc_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF grant standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.dc.dhs.tanf.grant_standard
        monthly = p.main[unit_size]
        return monthly * MONTHS_IN_YEAR
