from policyengine_us.model_api import *


class va_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF grant standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=47"

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.va.dss.tanf
        ceiling = min_(unit_size, p.max_unit_size)
        additional = unit_size - ceiling

        county = spm_unit.household("county_str", period)
        if_group3 = np.isin(county, p.localities.group3)
        main = where(
            if_group3,
            p.grant_standard.group3.main[ceiling],
            p.grant_standard.group2.main[ceiling],
        )
        addition = where(
            if_group3,
            p.grant_standard.group3.addition,
            p.grant_standard.group2.addition,
        )

        monthly = main + additional * addition
        return monthly * MONTHS_IN_YEAR
