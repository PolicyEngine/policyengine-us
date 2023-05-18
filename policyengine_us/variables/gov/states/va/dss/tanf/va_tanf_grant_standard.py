from policyengine_us.model_api import *


class va_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF grant standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        ceiling = min_(unit_size, 10)
        additional = unit_size - ceiling

        county = spm_unit.household("county_str", period)
        p = parameters(period).gov.states.va.dss.tanf
        if_group3 = county in p.localities.group3
        p = where(
            if_group3,
            p.grant_standard.group3,
            p.grant_standard.group2,
        )

        monthly = p.main[ceiling] + additional * p.addition
        return monthly * MONTHS_IN_YEAR
