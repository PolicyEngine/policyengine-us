from policyengine_us.model_api import *


class ny_ccap_family_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "New York CCAP monthly family share"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://www.acf.hhs.gov/sites/default/files/documents/occ/NY-Accepted-ACF118-CCDF-FFY-2025-2027-Appendix.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        income = spm_unit("ccdf_income", period)
        fpl = spm_unit("spm_unit_fpg", period)
        income_exceeding_fpl = max_(income - fpl, 0)
        p = parameters(period).gov.states.ny.ocfs.ccap

        if p.statewide_family_share_in_effect:
            family_share_rate = p.family_share_rate
        else:
            family_share_rate = p.historical_family_share_rate
        calculated_share = income_exceeding_fpl * family_share_rate
        minimum_share = p.minimum_weekly_family_share * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        # 18 NYCRR 415.3(e)(1) exempts families with income at or below the
        # poverty level from any family share; the $1 weekly minimum under
        # 415.3(e)(4) applies only to families paying an income-based share.
        return where(
            income > fpl,
            max_(calculated_share, minimum_share),
            0,
        )
