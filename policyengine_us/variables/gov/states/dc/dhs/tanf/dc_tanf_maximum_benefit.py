from policyengine_us.model_api import *


class dc_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF maximum benefit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.dc.dhs.tanf.maximum_benefit
        monthly = p.main[unit_size]
        return monthly * MONTHS_IN_YEAR
