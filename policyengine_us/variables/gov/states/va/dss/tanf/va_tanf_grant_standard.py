from policyengine_us.model_api import *


class va_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF grant standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/tanfx2fview/tanf/Chapter-300---Need-and-Amount-of-Assistance.pdf#page=51"

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.va.dss.tanf
        p_grant_standard = p.payment.grant_standard
        ceiling = min_(unit_size, p.max_unit_size)
        additional = unit_size - ceiling

        county = spm_unit.household("county_str", period)
        if_group3 = np.isin(county, p.localities.group3)
        main = where(
            if_group3,
            p_grant_standard.group3.main[ceiling],
            p_grant_standard.group2.main[ceiling],
        )
        addition = where(
            if_group3,
            p_grant_standard.group3.addition,
            p_grant_standard.group2.addition,
        )

        amount = main + additional * addition
        # The tables hold the printed Section 304, Appendix 2 standards from
        # July 2020. Earlier periods scale the July 2020 standards by the
        # standard multiplier, which is below 1 only before July 2020.
        return amount * min_(p.standard_multiplier, 1)
