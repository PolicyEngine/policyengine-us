from policyengine_us.model_api import *


class va_tanf_up_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF UP grant standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=47"

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.va.dss.tanf
        # Access July 2020 base values
        p_up_grant_standard = (
            parameters.gov.states.va.dss.tanf.payment.up_grant_standard(
                f"2020-10-01"
            )
        )
        ceiling = min_(unit_size, p.max_unit_size)
        additional = unit_size - ceiling

        county = spm_unit.household("county_str", period)
        if_group3 = np.isin(county, p.localities.group3)
        main = where(
            if_group3,
            p_up_grant_standard.group3.main[ceiling],
            p_up_grant_standard.group2.main[ceiling],
        )
        addition = where(
            if_group3,
            p_up_grant_standard.group3.addition,
            p_up_grant_standard.group2.addition,
        )

        base_amount = main + additional * addition
        # Apply standard multiplier for increases since July 2020 base

        return base_amount * p.standard_multiplier
